"""Standard-library unit tests for Termux runit service adapter static contract."""

from __future__ import annotations

import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import unittest

# Ensure src is on sys.path
_src_dir = Path(__file__).resolve().parent.parent / "src"
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))


class TestTermuxServiceAdapterFile(unittest.TestCase):
    """AC1: Service run file existence, LF formatting, and executable permissions."""

    def setUp(self) -> None:
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.run_file_path = (
            self.workspace_root / "deploy" / "termux" / "services" / "aios-node" / "run"
        )

    def test_run_file_exists_and_non_empty(self) -> None:
        self.assertTrue(
            self.run_file_path.is_file(),
            f"Expected service run file at {self.run_file_path}",
        )
        self.assertGreater(
            self.run_file_path.stat().st_size,
            0,
            "Service run file must not be empty",
        )

    def test_run_file_uses_lf_line_endings(self) -> None:
        raw_bytes = self.run_file_path.read_bytes()
        self.assertNotIn(
            b"\r\n",
            raw_bytes,
            "Service run file must use POSIX LF line endings, never Windows CRLF",
        )
        self.assertTrue(
            raw_bytes.endswith(b"\n"),
            "Service run file must terminate with a newline",
        )

    def test_run_file_git_executable_mode(self) -> None:
        """Constraint: The committed run file must have executable Git mode (100755)."""
        # On POSIX hosts, check file system permission bits directly
        if os.name != "nt":
            mode = self.run_file_path.stat().st_mode
            self.assertTrue(
                bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)),
                "Service run file must have executable permission bits on POSIX systems",
            )

        # On all hosts with git available, check the git index mode
        try:
            rel_path = "deploy/termux/services/aios-node/run"
            result = subprocess.run(
                ["git", "ls-files", "-s", rel_path],
                cwd=str(self.workspace_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                # Format: <mode> <blob-sha> <stage> <path>
                file_mode = result.stdout.strip().split()[0]
                self.assertEqual(
                    file_mode,
                    "100755",
                    f"Git index mode for {rel_path} must be 100755, got {file_mode}",
                )
        except (FileNotFoundError, OSError):
            pass

    def test_run_file_shebang_is_native_termux_shell(self) -> None:
        lines = self.run_file_path.read_text(encoding="utf-8").splitlines()
        self.assertTrue(len(lines) > 0, "Run file has no lines")
        shebang = lines[0].strip()
        self.assertEqual(
            shebang,
            "#!/data/data/com.termux/files/usr/bin/sh",
            "Shebang must point to native Termux shell /data/data/com.termux/files/usr/bin/sh",
        )


class TestTermuxServiceAdapterExecutionContract(unittest.TestCase):
    """AC1 & AC2: Single process execution, environment overrides, and bounded inputs."""

    def setUp(self) -> None:
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.run_file_path = (
            self.workspace_root / "deploy" / "termux" / "services" / "aios-node" / "run"
        )
        self.content = self.run_file_path.read_text(encoding="utf-8")
        self.lines = self.content.splitlines()
        # Collect non-empty non-comment lines
        self.code_lines = [
            line.strip()
            for line in self.lines
            if line.strip() and not line.strip().startswith("#")
        ]

    def test_exec_replaces_shell_with_single_host_process(self) -> None:
        """AC1: Uses `exec` to start exactly one `aios-node host` process."""
        # Check stderr redirect
        self.assertIn("exec 2>&1", self.code_lines)

        # Normalize line continuations (\ at end of line)
        full_command = " ".join(
            line.rstrip("\\").strip()
            for line in self.lines
            if not line.strip().startswith("#")
        )

        exec_matches = re.findall(r'\bexec\s+("\$AIOS_NODE_BIN"|aios-node|\S+)\s+host\b', full_command)
        self.assertEqual(
            len(exec_matches),
            1,
            f"Expected exactly one `exec <bin> host` command in run file, found: {exec_matches}",
        )

        # Verify it does not background the host process
        self.assertFalse(
            any("&" in line for line in self.code_lines if "host" in line),
            "Host process execution must not be backgrounded with &",
        )

    def test_no_internal_loop_or_polling_or_sleep(self) -> None:
        """AC1: Contains no internal restart, retry, sleep, or polling loop."""
        forbidden_control_structures = ["while ", "until ", "for ", "sleep ", "retry"]
        for line in self.code_lines:
            lower = line.lower()
            for pattern in forbidden_control_structures:
                self.assertNotIn(
                    pattern,
                    lower,
                    f"Forbidden control structure '{pattern}' found in service run file line: {line}",
                )

    def test_deterministic_environment_defaults(self) -> None:
        """AC2: Exposes deterministic environment-overridable paths with Mi 10 Pro defaults."""
        text = self.content

        # Check PREFIX and HOME defaults
        self.assertIn('PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"', text)
        self.assertIn('HOME="${HOME:-/data/data/com.termux/files/home}"', text)

        # Check AIOS-node executable override
        self.assertIn('AIOS_NODE_BIN="${AIOS_NODE_BIN:-$PREFIX/bin/aios-node}"', text)

        # Check Host-state directory override
        self.assertIn(
            'AIOS_NODE_STATE_DIR="${AIOS_NODE_STATE_DIR:-$HOME/.aios-node/state}"',
            text,
        )

        # Check Pinned AIOS-renew executable override
        self.assertIn(
            'AIOS_NODE_AIOS_BIN="${AIOS_NODE_AIOS_BIN:-${AIOS_BIN:-$HOME/.venvs/aios-renew-5bdaa603/bin/aios}}"',
            text,
        )

        # Check Antigravity executable override
        self.assertIn(
            'AIOS_NODE_ANTIGRAVITY_BIN="${AIOS_NODE_ANTIGRAVITY_BIN:-${ANTIGRAVITY_BIN:-${AGY_BIN:-$PREFIX/bin/agy}}}"',
            text,
        )

    def test_paths_passed_as_bounded_readiness_cli_configuration(self) -> None:
        """AC2: Passes dependencies only as bounded readiness configuration to host CLI."""
        joined = " ".join(line.rstrip("\\").strip() for line in self.lines if not line.strip().startswith("#"))

        # Must pass --state-dir, --aios-bin, and --antigravity-bin
        self.assertIn('--state-dir "$AIOS_NODE_STATE_DIR"', joined)
        self.assertIn('--aios-bin "$AIOS_NODE_AIOS_BIN"', joined)
        self.assertIn('--antigravity-bin "$AIOS_NODE_ANTIGRAVITY_BIN"', joined)

        # Must NOT pass --once (host must remain running under runit supervision)
        self.assertNotIn("--once", joined)

        # Must NOT directly execute $AIOS_NODE_AIOS_BIN or $AIOS_NODE_ANTIGRAVITY_BIN
        self.assertNotRegex(joined, r'(?<!-bin )"\$AIOS_NODE_AIOS_BIN"')
        self.assertNotRegex(joined, r'(?<!-bin )"\$AIOS_NODE_ANTIGRAVITY_BIN"')


class TestTermuxServiceStaticContractProhibitions(unittest.TestCase):
    """AC3: Static contract tests proving absence of unauthorized operations."""

    def setUp(self) -> None:
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.run_file_path = (
            self.workspace_root / "deploy" / "termux" / "services" / "aios-node" / "run"
        )
        self.content = self.run_file_path.read_text(encoding="utf-8")
        self.executable_text = "\n".join(
            line for line in self.content.splitlines() if not line.strip().startswith("#")
        )

    def test_no_direct_executor_invocations(self) -> None:
        """AC3: Contains no direct Executor invocation (agy, antigravity, codex)."""
        # Forbidden executor execution patterns in executable text
        forbidden_executors = [
            r"\bagy\s",
            r"\bantigravity\s",
            r"\bcodex\b",
            r"\$PREFIX/bin/agy\s",
        ]
        for pattern in forbidden_executors:
            self.assertFalse(
                re.search(pattern, self.executable_text),
                f"Direct Executor execution pattern '{pattern}' found in service run file",
            )

    def test_no_canonical_aios_operations(self) -> None:
        """AC3: Contains no canonical AIOS operations (aios run, remediate, repair)."""
        forbidden_operations = [
            r"\baios\s+run\b",
            r"\baios\s+remediate\b",
            r"\baios\s+repair\b",
            r"\baios\s+task\b",
            r"\baios\s+review\b",
            r"\baios\s+publish\b",
        ]
        for pattern in forbidden_operations:
            self.assertFalse(
                re.search(pattern, self.executable_text, re.IGNORECASE),
                f"Canonical AIOS operation '{pattern}' found in service run file",
            )

    def test_no_git_mutation_commands(self) -> None:
        """AC3: Contains no Git mutation commands."""
        forbidden_git = [
            r"\bgit\s+commit\b",
            r"\bgit\s+push\b",
            r"\bgit\s+pull\b",
            r"\bgit\s+checkout\b",
            r"\bgit\s+reset\b",
            r"\bgit\s+rebase\b",
            r"\bgit\s+merge\b",
            r"\bgit\s+stash\b",
            r"\bgit\s+branch\b",
        ]
        for pattern in forbidden_git:
            self.assertFalse(
                re.search(pattern, self.executable_text),
                f"Git mutation command '{pattern}' found in service run file",
            )

    def test_no_project_verification_commands(self) -> None:
        """AC3: Contains no project verification commands."""
        forbidden_verification = [
            r"\bpytest\b",
            r"\bunittest\b",
            r"\bcompileall\b",
            r"\bcargo\b",
            r"\bnpm\s+test\b",
            r"\bmake\b",
        ]
        for pattern in forbidden_verification:
            self.assertFalse(
                re.search(pattern, self.executable_text),
                f"Project verification command '{pattern}' found in service run file",
            )

    def test_no_network_or_model_calls(self) -> None:
        """AC3: Contains no network or model calls."""
        forbidden_network = [
            r"\bcurl\b",
            r"\bwget\b",
            r"\bnc\b",
            r"\bfetch\b",
            r"\burllib\b",
            r"\brequests\b",
            r"https?://",
        ]
        for pattern in forbidden_network:
            self.assertFalse(
                re.search(pattern, self.executable_text, re.IGNORECASE),
                f"Network/model call pattern '{pattern}' found in service run file",
            )

    def test_no_wake_lock_actions(self) -> None:
        """AC3 & Constraints: Service run file must not invoke termux-wake-lock."""
        self.assertNotIn("termux-wake-lock", self.content)
        self.assertNotIn("termux-wake-unlock", self.content)

    def test_no_service_enable_disable_actions(self) -> None:
        """AC3 & Constraints: Service run file must not enable or disable itself."""
        forbidden_service_commands = [
            r"\bsv-enable\b",
            r"\bsv-disable\b",
            r"\bsv\s+up\b",
            r"\bsv\s+down\b",
            r"\bsv\s+restart\b",
        ]
        for pattern in forbidden_service_commands:
            self.assertFalse(
                re.search(pattern, self.executable_text),
                f"Service enable/disable action '{pattern}' found in service run file",
            )

    def test_no_termux_boot_commands(self) -> None:
        """AC3 & Constraints: Service run file must not call Termux:Boot."""
        forbidden_boot = [
            r"\btermux-boot\b",
            r"\.termux/boot",
        ]
        for pattern in forbidden_boot:
            self.assertFalse(
                re.search(pattern, self.executable_text),
                f"Termux:Boot pattern '{pattern}' found in service run file",
            )


class TestArchitecturalBoundary(unittest.TestCase):
    """Constraints: Platform paths in adapter must not leak into portable core."""

    def setUp(self) -> None:
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.src_aios_node = self.workspace_root / "src" / "aios_node"

    def test_no_termux_paths_in_src_aios_node(self) -> None:
        termux_signature = "/data/data/com.termux"
        for py_file in self.src_aios_node.rglob("*.py"):
            text = py_file.read_text(encoding="utf-8")
            self.assertNotIn(
                termux_signature,
                text,
                f"Termux-specific path leaked into core file: {py_file}",
            )


class TestDocumentationContract(unittest.TestCase):
    """AC4: Documentation captures destination, configuration boundary, and rules."""

    def setUp(self) -> None:
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.doc_path = self.workspace_root / "docs" / "N4-TERMUX-RUNIT-ADAPTER.md"

    def test_documentation_file_exists(self) -> None:
        self.assertTrue(self.doc_path.is_file(), f"Expected doc at {self.doc_path}")

    def test_documentation_specifies_destination(self) -> None:
        doc = self.doc_path.read_text(encoding="utf-8")
        self.assertIn("$PREFIX/var/service/aios-node", doc)
        self.assertIn("deploy/termux/services/aios-node/run", doc)

    def test_documentation_specifies_configuration_boundary(self) -> None:
        doc = self.doc_path.read_text(encoding="utf-8")
        self.assertIn("AIOS_NODE_BIN", doc)
        self.assertIn("AIOS_NODE_STATE_DIR", doc)
        self.assertIn("AIOS_NODE_AIOS_BIN", doc)
        self.assertIn("AIOS_NODE_ANTIGRAVITY_BIN", doc)
        self.assertIn("bounded readiness-probe", doc.lower())

    def test_documentation_specifies_node003_activation(self) -> None:
        doc = self.doc_path.read_text(encoding="utf-8")
        self.assertIn("NODE-003", doc)
        self.assertIn("sv-enable", doc)

    def test_documentation_states_supervision_rule(self) -> None:
        doc = self.doc_path.read_text(encoding="utf-8")
        # Must explicitly state runit supervises only host availability rather than engineering execution
        self.assertTrue(
            "host availability" in doc.lower() and "engineering execution" in doc.lower(),
            "Documentation must explicitly distinguish host availability from engineering execution",
        )
        # Must explicitly state runit may restart the host process but never canonical AIOS work
        self.assertIn("restart the AIOS-node host process", doc)
        self.assertIn("authority to restart canonical AIOS work", doc)


if __name__ == "__main__":
    unittest.main()
