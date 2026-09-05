"""Standard-library unit tests for AIOS-node host core, lifecycle, and CLI."""

from __future__ import annotations

import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import threading
import time
import tomllib
import unittest
from unittest.mock import patch

# Ensure src is on sys.path
_src_dir = Path(__file__).resolve().parent.parent / "src"
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

from aios_node import (
    Host,
    HostConfig,
    HostState,
    OperationalState,
    ReasonCode,
    __version__,
    load_state,
    persist_state,
)
from aios_node.cli import main
from aios_node.host import (
    PROHIBITED_ENGINEERING_FIELDS,
    SCHEMA_VERSION,
    check_executable_path,
    check_state_dir,
)


class TestPyprojectAndPackage(unittest.TestCase):
    """AC1: pyproject.toml defines installable Python 3.11+ package and entry point."""

    def setUp(self) -> None:
        self.workspace_root = Path(__file__).resolve().parent.parent
        self.pyproject_path = self.workspace_root / "pyproject.toml"

    def test_pyproject_definition(self) -> None:
        self.assertTrue(self.pyproject_path.exists(), "pyproject.toml must exist")
        with open(self.pyproject_path, "rb") as f:
            data = tomllib.load(f)

        project = data.get("project", {})
        self.assertEqual(project.get("name"), "aios-node")
        self.assertIn(">=3.11", project.get("requires-python", ""))

        scripts = project.get("scripts", {})
        self.assertEqual(scripts.get("aios-node"), "aios_node.cli:main")

    def test_version_exposed(self) -> None:
        self.assertIsInstance(__version__, str)
        self.assertTrue(len(__version__) > 0)


class TestOperationalStateAndModel(unittest.TestCase):
    """AC4 & AC6: Operational state semantics and schema validation."""

    def test_ready_state_creation(self) -> None:
        state = HostState(
            schema_version=SCHEMA_VERSION,
            operational_state=OperationalState.READY,
            reasons=(),
            process_id=os.getpid(),
        )
        self.assertEqual(state.operational_state, "READY")
        self.assertEqual(state.reasons, ())
        self.assertEqual(state.pid, os.getpid())

        data = state.to_dict()
        expected_keys = {"schema_version", "operational_state", "reasons", "process_id"}
        self.assertEqual(set(data.keys()), expected_keys)
        self.assertFalse(expected_keys.intersection(PROHIBITED_ENGINEERING_FIELDS))

    def test_degraded_state_creation(self) -> None:
        state = HostState(
            schema_version=SCHEMA_VERSION,
            operational_state=OperationalState.DEGRADED,
            reasons=("EXEC_NOT_FOUND:aios",),
            process_id=os.getpid(),
        )
        self.assertEqual(state.operational_state, "DEGRADED")
        self.assertEqual(state.reasons, ("EXEC_NOT_FOUND:aios",))

    def test_forbidden_states_rejected(self) -> None:
        # AC6: Core never locally emits BUSY or OFFLINE
        for forbidden in ("BUSY", "OFFLINE"):
            with self.assertRaises(ValueError) as ctx:
                HostState(
                    schema_version=SCHEMA_VERSION,
                    operational_state=forbidden,
                    reasons=(),
                    process_id=os.getpid(),
                )
            self.assertIn("forbidden", str(ctx.exception).lower())

    def test_invalid_states_rejected(self) -> None:
        with self.assertRaises(ValueError):
            HostState(
                schema_version=SCHEMA_VERSION,
                operational_state="UNKNOWN_STATE",
                reasons=(),
                process_id=os.getpid(),
            )

    def test_ready_cannot_have_reasons(self) -> None:
        with self.assertRaises(ValueError):
            HostState(
                schema_version=SCHEMA_VERSION,
                operational_state=OperationalState.READY,
                reasons=("SOME_REASON",),
                process_id=os.getpid(),
            )

    def test_degraded_requires_reasons(self) -> None:
        with self.assertRaises(ValueError):
            HostState(
                schema_version=SCHEMA_VERSION,
                operational_state=OperationalState.DEGRADED,
                reasons=(),
                process_id=os.getpid(),
            )

    def test_prohibited_engineering_fields_rejected_in_deserialization(self) -> None:
        for field_name in PROHIBITED_ENGINEERING_FIELDS:
            payload = {
                "schema_version": SCHEMA_VERSION,
                "operational_state": OperationalState.READY,
                "reasons": [],
                "process_id": 1234,
                field_name: "prohibited_value",
            }
            with self.assertRaises(ValueError) as ctx:
                HostState.from_dict(payload)
            self.assertIn("prohibited", str(ctx.exception).lower())

    def test_json_serialization_roundtrip(self) -> None:
        original = HostState(
            schema_version=SCHEMA_VERSION,
            operational_state=OperationalState.READY,
            reasons=(),
            process_id=9999,
        )
        raw_json = original.to_json()
        loaded = HostState.from_json(raw_json)
        self.assertEqual(original, loaded)


class TestReadinessProbing(unittest.TestCase):
    """AC2 & AC3: Deterministic readiness probing without external side effects."""

    def setUpself(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_dir = Path(self.temp_dir.name) / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_probe_ready_when_all_executable(self) -> None:
        self.setUpself()
        config = HostConfig(
            state_dir=self.state_dir,
            dependencies={"python": sys.executable},
        )
        host = Host(config=config)
        state = host.probe()
        self.assertEqual(state.operational_state, OperationalState.READY)
        self.assertEqual(state.reasons, ())

    def test_probe_degraded_when_dependency_missing(self) -> None:
        self.setUpself()
        missing_bin = self.state_dir / "nonexistent_binary_xyz"
        config = HostConfig(
            state_dir=self.state_dir,
            dependencies={
                "python": sys.executable,
                "aios": str(missing_bin),
            },
        )
        host = Host(config=config)
        state = host.probe()
        self.assertEqual(state.operational_state, OperationalState.DEGRADED)
        self.assertIn(ReasonCode.exec_not_found("aios"), state.reasons)

    def test_probe_degraded_when_dependency_not_executable(self) -> None:
        self.setUpself()
        non_exec_file = self.state_dir / "not_executable.txt"
        non_exec_file.write_text("dummy", encoding="utf-8")
        if os.name != "nt":
            non_exec_file.chmod(stat.S_IRUSR | stat.S_IWUSR)

        config = HostConfig(
            state_dir=self.state_dir,
            dependencies={"dummy": str(non_exec_file)},
        )
        host = Host(config=config)
        state = host.probe()
        self.assertEqual(state.operational_state, OperationalState.DEGRADED)
        self.assertIn(ReasonCode.exec_not_executable("dummy"), state.reasons)

    def test_probe_degraded_when_state_dir_is_a_file(self) -> None:
        self.setUpself()
        file_path = self.state_dir / "blocking_file"
        file_path.write_text("block", encoding="utf-8")

        config = HostConfig(state_dir=file_path)
        host = Host(config=config)
        state = host.probe()
        self.assertEqual(state.operational_state, OperationalState.DEGRADED)
        self.assertIn(ReasonCode.STATE_DIR_NOT_DIRECTORY, state.reasons)

    def test_bounded_reason_ordering_deterministic(self) -> None:
        self.setUpself()
        config = HostConfig(
            state_dir=self.state_dir,
            dependencies={
                "zebra": self.state_dir / "missing_z",
                "alpha": self.state_dir / "missing_a",
            },
        )
        host = Host(config=config)
        state = host.probe()
        self.assertEqual(state.operational_state, OperationalState.DEGRADED)
        self.assertEqual(
            state.reasons,
            (ReasonCode.exec_not_found("alpha"), ReasonCode.exec_not_found("zebra")),
        )


class TestAtomicStatePersistence(unittest.TestCase):
    """AC4: Strict UTF-8 JSON and atomic same-directory replacement."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_dir = Path(self.temp_dir.name) / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.target_file = self.state_dir / "host_state.json"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_atomic_persistence_and_loading(self) -> None:
        state = HostState(
            schema_version=SCHEMA_VERSION,
            operational_state=OperationalState.READY,
            reasons=(),
            process_id=os.getpid(),
        )
        persisted_path = persist_state(state, self.target_file)
        self.assertEqual(persisted_path, self.target_file)
        self.assertTrue(self.target_file.exists())

        loaded = load_state(self.target_file)
        self.assertEqual(loaded, state)

        # Ensure no temporary files remained
        temp_files = list(self.state_dir.glob(".*.tmp*"))
        self.assertEqual(len(temp_files), 0)

    def test_atomic_replacement_overwrites_cleanly(self) -> None:
        state1 = HostState(
            schema_version=SCHEMA_VERSION,
            operational_state=OperationalState.READY,
            reasons=(),
            process_id=1111,
        )
        persist_state(state1, self.target_file)
        self.assertEqual(load_state(self.target_file).process_id, 1111)

        state2 = HostState(
            schema_version=SCHEMA_VERSION,
            operational_state=OperationalState.DEGRADED,
            reasons=("EXEC_NOT_FOUND:test",),
            process_id=2222,
        )
        persist_state(state2, self.target_file)
        loaded2 = load_state(self.target_file)
        self.assertEqual(loaded2.operational_state, OperationalState.DEGRADED)
        self.assertEqual(loaded2.process_id, 2222)


class TestHostLifecycleAndSignals(unittest.TestCase):
    """AC5: Non-polling idle lifecycle and clean termination."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_dir = Path(self.temp_dir.name) / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.config = HostConfig(
            state_dir=self.state_dir,
            dependencies={"python": sys.executable},
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_run_once_does_not_block(self) -> None:
        host = Host(config=self.config)
        state = host.run(once=True)
        self.assertEqual(state.operational_state, OperationalState.READY)
        self.assertTrue(self.config.state_file.exists())

    def test_idle_blocks_and_stops_on_request(self) -> None:
        host = Host(config=self.config)
        unblocked = threading.Event()

        def background_runner() -> None:
            host.idle(timeout=5.0)
            unblocked.set()

        thread = threading.Thread(target=background_runner)
        thread.start()

        time.sleep(0.05)
        self.assertFalse(unblocked.is_set(), "Host idle must block without busy-spinning")

        host.request_stop()
        thread.join(timeout=1.0)
        self.assertTrue(unblocked.is_set(), "Host must unblock immediately upon request_stop()")
        self.assertTrue(host.is_stopped)

    def test_no_aios_renew_imported(self) -> None:
        """Constraint: Must not import aios_renew."""
        self.assertNotIn("aios_renew", sys.modules)


class TestCLI(unittest.TestCase):
    """AC1: CLI commands and entry point behavior."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_dir = Path(self.temp_dir.name) / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_cli_probe_ready(self) -> None:
        stdout_capture = io.StringIO()
        with patch("sys.stdout", stdout_capture):
            exit_code = main([
                "probe",
                "--state-dir",
                str(self.state_dir),
                "--aios-bin",
                sys.executable,
            ])

        self.assertEqual(exit_code, 0)
        output = stdout_capture.getvalue()
        data = json.loads(output)
        self.assertEqual(data["operational_state"], "READY")

    def test_cli_probe_degraded(self) -> None:
        stdout_capture = io.StringIO()
        with patch("sys.stdout", stdout_capture):
            exit_code = main([
                "probe",
                "--state-dir",
                str(self.state_dir),
                "--aios-bin",
                str(self.state_dir / "missing_aios_bin"),
            ])

        self.assertEqual(exit_code, 1)
        output = stdout_capture.getvalue()
        data = json.loads(output)
        self.assertEqual(data["operational_state"], "DEGRADED")
        self.assertIn("EXEC_NOT_FOUND:aios", data["reasons"])

    def test_cli_host_once(self) -> None:
        exit_code = main([
            "host",
            "--once",
            "--state-dir",
            str(self.state_dir),
            "--aios-bin",
            sys.executable,
        ])
        self.assertEqual(exit_code, 0)
        state_file = self.state_dir / "host_state.json"
        self.assertTrue(state_file.exists())
        state = load_state(state_file)
        self.assertEqual(state.operational_state, "READY")


if __name__ == "__main__":
    unittest.main()
