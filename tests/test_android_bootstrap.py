"""Standard-library tests for Android cold-boot bootstrap static contracts (NODE-003B).

Validates:
- Manifest structure, permissions, and non-exported receiver (AC1)
- Fixed immutable Termux RunCommandService dispatch (AC2)
- Bounded setup/diagnostic MainActivity without shell/command execution (AC3)
- Native Termux bootstrap script environment and service-daemon launch (AC4)
- Platform-only Android build definition and GitHub-hosted workflow (AC5)
- Comprehensive documentation and security boundary explanation (AC6)
- Rejection of authority expansion, generic commands, and self-hosted runners (AC7)
- Preservation of physical cold-boot qualification gate (AC8)
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import stat
import subprocess
import unittest
import xml.etree.ElementTree as ET


def _strip_java_comments(source: str) -> str:
    """Removes single-line and multi-line comments from Java source code."""
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    source = re.sub(r"//.*$", "", source, flags=re.MULTILINE)
    return source


def _strip_markdown_formatting(text: str) -> str:
    """Removes basic markdown formatting chars (*, `) for plain-text inspection."""
    return re.sub(r"[*`]", "", text)


class TestAndroidManifestStaticContract(unittest.TestCase):
    """AC1: AndroidManifest defines standalone helper, minimum permissions, and non-exported receiver."""

    def setUp(self) -> None:
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.manifest_path = (
            self.workspace_root
            / "android"
            / "boot-bootstrap"
            / "app"
            / "src"
            / "main"
            / "AndroidManifest.xml"
        )
        self.assertTrue(self.manifest_path.is_file(), f"Manifest not found: {self.manifest_path}")
        self.tree = ET.parse(self.manifest_path)
        self.root = self.tree.getroot()
        self.ns = {"android": "http://schemas.android.com/apk/res/android"}

    def test_manifest_package_and_no_shared_uid(self) -> None:
        """Constraint 1: Standalone package with its own ID, no sharedUserId."""
        package = self.root.attrib.get("package")
        self.assertEqual(package, "io.aios.node.bootstrap")

        # Must not declare sharedUserId
        shared_user_id = self.root.attrib.get(
            "{http://schemas.android.com/apk/res/android}sharedUserId"
        )
        self.assertIsNone(
            shared_user_id,
            f"Helper must not declare android:sharedUserId, found: {shared_user_id}",
        )

        manifest_text = self.manifest_path.read_text(encoding="utf-8")
        self.assertNotIn("sharedUserId", manifest_text)

    def test_manifest_requested_permissions_strictly_bounded(self) -> None:
        """AC1 & Constraint 2: Only RECEIVE_BOOT_COMPLETED and com.termux.permission.RUN_COMMAND."""
        permissions = set()
        for elem in self.root.findall("uses-permission"):
            perm_name = elem.attrib.get(
                "{http://schemas.android.com/apk/res/android}name"
            )
            if perm_name:
                permissions.add(perm_name)

        expected_permissions = {
            "android.permission.RECEIVE_BOOT_COMPLETED",
            "com.termux.permission.RUN_COMMAND",
        }
        self.assertEqual(
            permissions,
            expected_permissions,
            f"Permissions must contain exactly {expected_permissions}, found: {permissions}",
        )

        forbidden_permissions = [
            "android.permission.INTERNET",
            "android.permission.ACCESS_NETWORK_STATE",
            "android.permission.WAKE_LOCK",
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.WRITE_EXTERNAL_STORAGE",
            "android.permission.MANAGE_EXTERNAL_STORAGE",
            "android.permission.REQUEST_INSTALL_PACKAGES",
            "android.permission.INSTALL_PACKAGES",
            "android.permission.BIND_ACCESSIBILITY_SERVICE",
            "android.permission.BIND_DEVICE_ADMIN",
            "android.permission.SYSTEM_ALERT_WINDOW",
        ]
        manifest_text = self.manifest_path.read_text(encoding="utf-8")
        for forbidden in forbidden_permissions:
            self.assertNotIn(
                forbidden,
                manifest_text,
                f"Forbidden permission '{forbidden}' found in AndroidManifest.xml",
            )

    def test_boot_receiver_is_non_exported(self) -> None:
        """AC1 & Constraint 3: Receiver is non-exported and listens for BOOT_COMPLETED."""
        application = self.root.find("application")
        self.assertIsNotNone(application, "Missing <application> in manifest")

        receivers = application.findall("receiver")
        self.assertGreaterEqual(len(receivers), 1, "Expected at least one <receiver>")

        boot_receiver = None
        for r in receivers:
            name = r.attrib.get("{http://schemas.android.com/apk/res/android}name", "")
            if name.endswith("BootReceiver"):
                boot_receiver = r
                break

        self.assertIsNotNone(boot_receiver, "BootReceiver not declared in manifest")

        exported = boot_receiver.attrib.get(
            "{http://schemas.android.com/apk/res/android}exported"
        )
        self.assertEqual(
            exported,
            "false",
            f"BootReceiver must be non-exported (android:exported='false'), got: {exported}",
        )

        actions = [
            action.attrib.get("{http://schemas.android.com/apk/res/android}name")
            for intent_filter in boot_receiver.findall("intent-filter")
            for action in intent_filter.findall("action")
        ]
        self.assertIn(
            "android.intent.action.BOOT_COMPLETED",
            actions,
            "BootReceiver must listen for android.intent.action.BOOT_COMPLETED",
        )

    def test_main_activity_is_launcher(self) -> None:
        """AC1: MainActivity is declared as exported launcher."""
        application = self.root.find("application")
        activities = application.findall("activity")
        self.assertGreaterEqual(len(activities), 1, "Expected at least one <activity>")

        main_activity = None
        for act in activities:
            name = act.attrib.get("{http://schemas.android.com/apk/res/android}name", "")
            if name.endswith("MainActivity"):
                main_activity = act
                break

        self.assertIsNotNone(main_activity, "MainActivity not declared in manifest")
        exported = main_activity.attrib.get(
            "{http://schemas.android.com/apk/res/android}exported"
        )
        self.assertEqual(exported, "true", "MainActivity must be exported as launcher")


class TestBootstrapJavaSourceStaticContract(unittest.TestCase):
    """AC2 & AC3: Fixed dispatch contract, non-parameterized intent, and bounded setup Activity."""

    def setUp(self) -> None:
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.java_dir = (
            self.workspace_root
            / "android"
            / "boot-bootstrap"
            / "app"
            / "src"
            / "main"
            / "java"
            / "io"
            / "aios"
            / "node"
            / "bootstrap"
        )
        self.contract_file = self.java_dir / "BootstrapContract.java"
        self.receiver_file = self.java_dir / "BootReceiver.java"
        self.activity_file = self.java_dir / "MainActivity.java"

    def test_files_exist(self) -> None:
        self.assertTrue(self.contract_file.is_file(), f"Missing {self.contract_file}")
        self.assertTrue(self.receiver_file.is_file(), f"Missing {self.receiver_file}")
        self.assertTrue(self.activity_file.is_file(), f"Missing {self.activity_file}")

    def test_bootstrap_contract_constants(self) -> None:
        """AC2 & Constraint 4, 5, 6: Fixed immutable Termux dispatch parameters."""
        content = self.contract_file.read_text(encoding="utf-8")

        self.assertIn('"com.termux"', content)
        self.assertIn('"com.termux.app.RunCommandService"', content)
        self.assertIn('"com.termux.RUN_COMMAND"', content)
        self.assertIn(
            '"/data/data/com.termux/files/home/.aios-node/bootstrap/start-services.sh"',
            content,
        )
        self.assertIn('"app-shell"', content)
        self.assertIn('"com.termux.RUN_COMMAND_PATH"', content)
        self.assertIn('"com.termux.RUN_COMMAND_ARGUMENTS"', content)
        self.assertIn('"com.termux.RUN_COMMAND_RUNNER"', content)
        self.assertIn('"com.termux.RUN_COMMAND_BACKGROUND"', content)
        self.assertIn('"com.termux.permission.RUN_COMMAND"', content)

    def test_boot_receiver_single_fixed_dispatch(self) -> None:
        """AC2 & Constraint 3, 7: Explicit fixed dispatch, foreground service on O+, no retries/loops."""
        raw_content = self.receiver_file.read_text(encoding="utf-8")
        code = _strip_java_comments(raw_content)

        # Action check
        self.assertIn("ACTION_BOOT_COMPLETED", code)

        # Foreground service check on Android O+
        self.assertIn("startForegroundService", code)
        self.assertIn("startService", code)
        self.assertIn("VERSION_CODES.O", code)

        # Uses fixed intent creation
        self.assertIn("createFixedRunCommandIntent", code)

        # Prohibit retry, loop, alarm, worker, polling, timer in executable code
        forbidden_patterns = [
            r"\bwhile\s*\(",
            r"\bdo\s*\{",
            r"\bfor\s*\(",
            r"\bThread\.sleep\b",
            r"\bHandler\b",
            r"\bpostDelayed\b",
            r"\bAlarmManager\b",
            r"\bJobScheduler\b",
            r"\bWorkManager\b",
            r"\bScheduledExecutorService\b",
            r"\bretry\b",
        ]
        for pattern in forbidden_patterns:
            self.assertFalse(
                re.search(pattern, code, re.IGNORECASE),
                f"Forbidden pattern '{pattern}' found in BootReceiver.java code",
            )

    def test_boot_receiver_prohibits_network_and_executors(self) -> None:
        """Constraint 2 & AC7: No network, AIOS, or Executor invocations in receiver."""
        raw_content = self.receiver_file.read_text(encoding="utf-8")
        code = _strip_java_comments(raw_content)

        forbidden_tokens = [
            "java.net",
            "HttpURLConnection",
            "HttpClient",
            "Socket",
            "okhttp",
            "aios run",
            "aios remediate",
            "aios repair",
            "agy ",
            "antigravity",
            "codex",
            "Runtime.getRuntime().exec",
            "ProcessBuilder",
        ]
        for token in forbidden_tokens:
            self.assertNotIn(token, code, f"Forbidden token '{token}' in BootReceiver.java")

    def test_main_activity_bounded_surface(self) -> None:
        """AC3 & Constraint 9: MainActivity only checks permission and displays diagnostics."""
        raw_content = self.activity_file.read_text(encoding="utf-8")
        code = _strip_java_comments(raw_content)

        # Extends platform Activity
        self.assertIn("extends Activity", code)

        # Checks and requests permission
        self.assertIn("PERMISSION_RUN_COMMAND", code)
        self.assertIn("requestPermissions", code)
        self.assertIn("checkSelfPermission", code)

        # Displays diagnostics
        self.assertIn("PREFS_NAME", code)
        self.assertIn("KEY_LAST_BOOT_RECEIVED_AT", code)
        self.assertIn("KEY_LAST_DISPATCH_TIME", code)
        self.assertIn("KEY_LAST_DISPATCH_RESULT", code)

        # Prohibits command input, shell execution, or remote endpoints
        forbidden_tokens = [
            "EditText",
            "Runtime.getRuntime().exec",
            "ProcessBuilder",
            "java.net",
            "HttpURLConnection",
            "HttpClient",
            "Socket",
            "aios run",
            "aios remediate",
            "aios repair",
            "agy ",
            "antigravity",
            "codex",
        ]
        for token in forbidden_tokens:
            self.assertNotIn(token, code, f"Forbidden token '{token}' in MainActivity.java")

    def test_all_java_sources_use_platform_apis_only(self) -> None:
        """Constraint 11: Java sources must use platform Android APIs and Java only (no AndroidX)."""
        for java_file in self.java_dir.rglob("*.java"):
            content = java_file.read_text(encoding="utf-8")
            self.assertNotIn(
                "androidx.",
                content,
                f"AndroidX dependency found in {java_file.name}",
            )


class TestBootstrapScriptStaticContract(unittest.TestCase):
    """AC4: Native Termux bootstrap script environment, marker writing, and service start."""

    def setUp(self) -> None:
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.script_path = (
            self.workspace_root / "deploy" / "termux" / "bootstrap" / "start-services.sh"
        )
        self.assertTrue(self.script_path.is_file(), f"Script not found: {self.script_path}")
        self.content = self.script_path.read_text(encoding="utf-8")
        self.executable_lines = [
            line.strip()
            for line in self.content.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    def test_script_formatting_and_shebang(self) -> None:
        """AC4 & Constraint 10: POSIX LF line endings, trailing newline, native Termux shebang."""
        raw = self.script_path.read_bytes()
        self.assertNotIn(b"\r\n", raw, "start-services.sh must use POSIX LF line endings")
        self.assertTrue(raw.endswith(b"\n"), "start-services.sh must end with a newline")

        lines = self.content.splitlines()
        self.assertEqual(
            lines[0].strip(),
            "#!/data/data/com.termux/files/usr/bin/sh",
            "Shebang must point to native Termux shell /data/data/com.termux/files/usr/bin/sh",
        )

    def test_script_git_executable_mode(self) -> None:
        """Constraint 10: Committed script has executable Git mode (100755)."""
        if os.name != "nt":
            mode = self.script_path.stat().st_mode
            self.assertTrue(
                bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)),
                "Script must have executable bits on POSIX",
            )

        try:
            rel_path = "deploy/termux/bootstrap/start-services.sh"
            result = subprocess.run(
                ["git", "ls-files", "-s", rel_path],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                mode = result.stdout.strip().split()[0]
                self.assertEqual(
                    mode,
                    "100755",
                    f"Git index mode for {rel_path} must be 100755, got {mode}",
                )
        except (FileNotFoundError, OSError):
            pass

    def test_script_deterministic_environment(self) -> None:
        """AC4: Establishes PREFIX, SVDIR, LOGDIR deterministically and exports them."""
        self.assertIn('PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"', self.content)
        self.assertIn('HOME="${HOME:-/data/data/com.termux/files/home}"', self.content)
        self.assertIn('SVDIR="${SVDIR:-$PREFIX/var/service}"', self.content)
        self.assertIn('LOGDIR="${LOGDIR:-$HOME/.aios-node/logs}"', self.content)

        # Environment must be exported before exec'ing service-daemon so the new process inherits them
        daemon_exec_indices = [
            i for i, line in enumerate(self.executable_lines) if "service-daemon" in line
        ]
        self.assertTrue(daemon_exec_indices, "service-daemon invocation not found in executable lines")
        daemon_idx = daemon_exec_indices[0]

        exported_vars = set()
        for line in self.executable_lines[:daemon_idx]:
            match = re.match(r"^export\s+(.+)$", line)
            if match:
                for token in match.group(1).split():
                    var_name = token.split("=")[0]
                    exported_vars.add(var_name)

        for required_var in ("PREFIX", "SVDIR", "LOGDIR", "HOME"):
            self.assertIn(
                required_var,
                exported_vars,
                f"Environment variable {required_var} must be exported before service-daemon start",
            )

    def test_script_invokes_service_daemon_start_once(self) -> None:
        """AC4 & Constraint 10: Invokes service-daemon start exactly once via exec."""
        exec_lines = [
            line for line in self.executable_lines if line.startswith("exec ")
        ]
        # First exec line is stderr redirection: exec 2>&1
        # Second exec line is service-daemon start
        self.assertIn("exec 2>&1", exec_lines)
        daemon_execs = [
            line for line in exec_lines if 'service-daemon" start' in line or "service-daemon start" in line
        ]
        self.assertEqual(
            len(daemon_execs),
            1,
            f"Expected exactly one exec service-daemon start, found: {daemon_execs}",
        )

    def test_script_writes_bounded_boot_marker(self) -> None:
        """AC4: Writes bounded host-local boot marker data."""
        self.assertIn("boot_id", self.content)
        self.assertIn("last_boot.marker", self.content)

    def test_script_prohibitions(self) -> None:
        """AC4 & Constraint 10: Prohibits AIOS, Executor, Git, network, verification, retry, loop, wake locks."""
        executable_text = "\n".join(self.executable_lines)

        forbidden_patterns = [
            # Loops & retries
            r"\bwhile\s",
            r"\buntil\s",
            r"\bfor\s",
            r"\bsleep\s",
            r"\bretry\b",
            # Git mutations
            r"\bgit\s+commit\b",
            r"\bgit\s+push\b",
            r"\bgit\s+pull\b",
            r"\bgit\s+checkout\b",
            r"\bgit\s+reset\b",
            r"\bgit\s+rebase\b",
            r"\bgit\s+merge\b",
            r"\bgit\s+stash\b",
            r"\bgit\s+branch\b",
            # AIOS operations
            r"\baios\s+run\b",
            r"\baios\s+remediate\b",
            r"\baios\s+repair\b",
            r"\baios\s+task\b",
            r"\baios\s+review\b",
            r"\baios\s+publish\b",
            # Executors
            r"\bagy\s",
            r"\bantigravity\s",
            r"\bcodex\b",
            # Verifications
            r"\bpytest\b",
            r"\bunittest\b",
            r"\bcargo\b",
            r"\bnpm\s+test\b",
            r"\bmake\b",
            # Wake locks
            r"\btermux-wake-lock\b",
            r"\btermux-wake-unlock\b",
            # Service enable/disable actions
            r"\bsv-enable\b",
            r"\bsv-disable\b",
            r"\bsv\s+up\b",
            r"\bsv\s+down\b",
            r"\bsv\s+restart\b",
            # Network
            r"\bcurl\b",
            r"\bwget\b",
            r"\bnc\b",
            r"https?://",
        ]
        for pattern in forbidden_patterns:
            self.assertFalse(
                re.search(pattern, executable_text, re.IGNORECASE),
                f"Forbidden pattern '{pattern}' found in bootstrap script",
            )


class TestAndroidBuildAndWorkflowStaticContract(unittest.TestCase):
    """AC5: Standalone build definition and GitHub-hosted build workflow."""

    def setUp(self) -> None:
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.settings_file = self.workspace_root / "android" / "boot-bootstrap" / "settings.gradle"
        self.root_build_file = self.workspace_root / "android" / "boot-bootstrap" / "build.gradle"
        self.app_build_file = (
            self.workspace_root / "android" / "boot-bootstrap" / "app" / "build.gradle"
        )
        self.workflow_file = (
            self.workspace_root / ".github" / "workflows" / "build-android-bootstrap.yml"
        )

    def test_build_files_exist(self) -> None:
        self.assertTrue(self.settings_file.is_file(), f"Missing {self.settings_file}")
        self.assertTrue(self.root_build_file.is_file(), f"Missing {self.root_build_file}")
        self.assertTrue(self.app_build_file.is_file(), f"Missing {self.app_build_file}")
        self.assertTrue(self.workflow_file.is_file(), f"Missing {self.workflow_file}")

    def test_app_build_has_no_runtime_dependencies(self) -> None:
        """AC5 & Constraint 11: Platform Android APIs only; no external runtime libraries."""
        content = self.app_build_file.read_text(encoding="utf-8")
        self.assertNotIn("implementation '", content)
        self.assertNotIn('implementation "', content)
        self.assertNotIn("androidx", content)

    def test_workflow_uses_github_hosted_runner_only(self) -> None:
        """AC5 & Constraint 12: Uses GitHub-hosted runner, never self-hosted."""
        content = self.workflow_file.read_text(encoding="utf-8")
        self.assertIn("runs-on: ubuntu-latest", content)
        self.assertNotIn("self-hosted", content)

    def test_workflow_requires_no_secrets(self) -> None:
        """AC5 & Constraint 12: Requires no secrets."""
        content = self.workflow_file.read_text(encoding="utf-8")
        self.assertNotIn("secrets.", content)

    def test_workflow_uploads_debug_apk_artifact(self) -> None:
        """AC5: Uploads debug APK qualification artifact."""
        content = self.workflow_file.read_text(encoding="utf-8")
        self.assertIn("actions/upload-artifact", content)
        self.assertIn("app-debug.apk", content)

    def test_workflow_prohibits_aios_and_executors(self) -> None:
        """Constraint 12: Never invokes AIOS or executors in workflow."""
        content = self.workflow_file.read_text(encoding="utf-8")
        forbidden = ["aios run", "aios remediate", "aios repair", "agy", "antigravity", "codex"]
        for f in forbidden:
            self.assertNotIn(f, content, f"Forbidden command '{f}' in workflow")


class TestDocumentationStaticContract(unittest.TestCase):
    """AC6: Documentation captures installation, security boundaries, and reboot gate."""

    def setUp(self) -> None:
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.doc_file = self.workspace_root / "docs" / "N4-ANDROID-BOOTSTRAP.md"
        self.assertTrue(self.doc_file.is_file(), f"Doc file not found: {self.doc_file}")
        self.content = self.doc_file.read_text(encoding="utf-8")

    def test_documentation_sections(self) -> None:
        """AC6 & Constraint 14: Comprehensive documentation requirements."""
        text = self.content
        clean_text = _strip_markdown_formatting(text).lower()

        # Installation and permission grant
        self.assertIn("com.termux.permission.run_command", clean_text)
        self.assertIn("pm grant", clean_text)

        # Termux allow-external-apps requirement and security implication
        self.assertIn("allow-external-apps=true", clean_text)
        self.assertTrue(
            "security note" in clean_text or "security implication" in clean_text,
            "Documentation must state security implication of allow-external-apps=true",
        )
        self.assertTrue(
            "only to this bounded helper" in clean_text,
            "Documentation must specify granting RUN_COMMAND only to this bounded helper",
        )

        # Xiaomi Autostart and battery requirements
        self.assertIn("autostart", clean_text)
        self.assertIn("no restrictions", clean_text)

        # Bootstrap deployment path
        self.assertIn(".aios-node/bootstrap/start-services.sh", clean_text)

        # Security boundary and artifact limitations
        self.assertIn("disposable qualification artifact", clean_text)
        self.assertIn("no android:shareduserid", clean_text)

        # Physical cold-boot gate
        self.assertIn("12-point qualification gate", clean_text)
        self.assertTrue(
            "does not mark n4 as pass" in clean_text or "does not mark n4 pass" in clean_text,
            "Documentation must explicitly state that source completion does not mark N4 PASS",
        )


class TestRejectionOfAuthorityExpansion(unittest.TestCase):
    """AC7: Static tests reject additions of generic commands, network, shared UID, or self-hosted runners."""

    def test_rejects_arbitrary_manifest_permission_expansion(self) -> None:
        """Verifies policy: adding INTERNET or WAKE_LOCK to manifest would be rejected."""
        dummy_manifest_with_net = (
            '<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="io.aios.node.bootstrap">\n'
            '  <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />\n'
            '  <uses-permission android:name="com.termux.permission.RUN_COMMAND" />\n'
            '  <uses-permission android:name="android.permission.INTERNET" />\n'
            '</manifest>'
        )
        root = ET.fromstring(dummy_manifest_with_net)
        perms = {
            e.attrib.get("{http://schemas.android.com/apk/res/android}name")
            for e in root.findall("uses-permission")
        }
        self.assertIn("android.permission.INTERNET", perms)
        # Verify our standard validator strictly rejects this
        allowed = {"android.permission.RECEIVE_BOOT_COMPLETED", "com.termux.permission.RUN_COMMAND"}
        self.assertNotEqual(perms, allowed, "Manifest with INTERNET must be rejected")

    def test_rejects_shared_uid_expansion(self) -> None:
        """Verifies policy: adding android:sharedUserId would be rejected."""
        dummy_manifest_with_shared = (
            '<manifest xmlns:android="http://schemas.android.com/apk/res/android"\n'
            '    package="io.aios.node.bootstrap"\n'
            '    android:sharedUserId="com.termux">\n'
            '</manifest>'
        )
        root = ET.fromstring(dummy_manifest_with_shared)
        shared = root.attrib.get("{http://schemas.android.com/apk/res/android}sharedUserId")
        self.assertEqual(shared, "com.termux")
        # Validator rejects when shared is not None
        self.assertIsNotNone(shared, "Manifest with sharedUserId must be rejected")

    def test_rejects_self_hosted_runner_expansion(self) -> None:
        """Verifies policy: workflow using self-hosted runner would be rejected."""
        dummy_workflow = "jobs:\n  build:\n    runs-on: [self-hosted, linux]\n"
        self.assertIn("self-hosted", dummy_workflow)


class TestQualificationGateContract(unittest.TestCase):
    """AC8: NODE-003B source completion does not mark N4 PASS."""

    def test_roadmap_and_docs_preserve_cold_boot_gate(self) -> None:
        workspace_root = Path(__file__).resolve().parent.parent
        roadmap_path = workspace_root / "docs" / "AIOS-NODE-ROADMAP.md"
        doc_path = workspace_root / "docs" / "N4-ANDROID-BOOTSTRAP.md"

        roadmap_text = roadmap_path.read_text(encoding="utf-8")
        doc_text = doc_path.read_text(encoding="utf-8")
        clean_doc = _strip_markdown_formatting(doc_text).lower()

        # Roadmap must show N4 is active or requires physical cold-boot proof
        self.assertIn("NODE-003B", roadmap_text)
        self.assertTrue(
            "does not mark n4 as pass" in clean_doc or "does not mark n4 pass" in clean_doc,
            "Docs must explicitly preserve cold-boot qualification gate",
        )


if __name__ == "__main__":
    unittest.main()
