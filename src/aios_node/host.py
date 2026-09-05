"""Host core: Lifecycle, readiness probing, and atomic state persistence for AIOS-node."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import signal
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Any

SCHEMA_VERSION: str = "1.0"


class OperationalState:
    """Operational state vocabulary for AIOS-node host core."""

    READY = "READY"
    DEGRADED = "DEGRADED"

    ALLOWED_LOCAL_STATES = frozenset({READY, DEGRADED})
    FORBIDDEN_LOCAL_STATES = frozenset({"BUSY", "OFFLINE"})


class ReasonCode:
    """Bounded operational reason codes."""

    PYTHON_VERSION_INCOMPATIBLE = "PYTHON_VERSION_INCOMPATIBLE"
    STATE_DIR_NOT_WRITABLE = "STATE_DIR_NOT_WRITABLE"
    STATE_DIR_NOT_DIRECTORY = "STATE_DIR_NOT_DIRECTORY"
    STATE_DIR_CREATE_FAILED = "STATE_DIR_CREATE_FAILED"
    EXEC_NOT_FOUND_PREFIX = "EXEC_NOT_FOUND:"
    EXEC_NOT_EXECUTABLE_PREFIX = "EXEC_NOT_EXECUTABLE:"

    @classmethod
    def exec_not_found(cls, name: str) -> str:
        return f"{cls.EXEC_NOT_FOUND_PREFIX}{name}"

    @classmethod
    def exec_not_executable(cls, name: str) -> str:
        return f"{cls.EXEC_NOT_EXECUTABLE_PREFIX}{name}"


PROHIBITED_ENGINEERING_FIELDS = frozenset({
    "task_id",
    "run_id",
    "head_sha",
    "base_sha",
    "result",
    "evidence",
    "verdict",
    "status",
    "pass",
    "fail",
    "review",
    "remediation",
    "repair",
    "publication",
    "claims",
    "unresolved",
    "changed_files",
})


@dataclass(frozen=True)
class HostState:
    """Operational host-state snapshot.
    
    Contains only host operational fields and schema metadata.
    Must never contain engineering verdicts or canonical workflow fields.
    """

    schema_version: str = SCHEMA_VERSION
    operational_state: str = OperationalState.READY
    reasons: tuple[str, ...] = ()
    process_id: int = field(default_factory=os.getpid)

    def __post_init__(self) -> None:
        if self.operational_state in OperationalState.FORBIDDEN_LOCAL_STATES:
            raise ValueError(
                f"N4 host core may only emit READY or DEGRADED; "
                f"'{self.operational_state}' is forbidden in host core."
            )
        if self.operational_state not in OperationalState.ALLOWED_LOCAL_STATES:
            raise ValueError(f"Invalid operational state: '{self.operational_state}'")
        if not isinstance(self.reasons, tuple):
            object.__setattr__(self, "reasons", tuple(self.reasons))
        if self.operational_state == OperationalState.READY and len(self.reasons) > 0:
            raise ValueError("Operational state cannot be READY when reasons are present")
        if self.operational_state == OperationalState.DEGRADED and len(self.reasons) == 0:
            raise ValueError("Operational state DEGRADED requires at least one reason code")
        if not isinstance(self.process_id, int) or self.process_id <= 0:
            raise ValueError(f"process_id must be a positive integer, got {self.process_id}")
        if not self.schema_version or not isinstance(self.schema_version, str):
            raise ValueError("schema_version must be a non-empty string")

    @property
    def pid(self) -> int:
        return self.process_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "operational_state": self.operational_state,
            "reasons": list(self.reasons),
            "process_id": self.process_id,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False) + "\n"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HostState:
        for field_name in PROHIBITED_ENGINEERING_FIELDS:
            if field_name in data:
                raise ValueError(f"Prohibited engineering field '{field_name}' in host state data")
        pid = data.get("process_id", data.get("pid", os.getpid()))
        return cls(
            schema_version=str(data.get("schema_version", SCHEMA_VERSION)),
            operational_state=str(data.get("operational_state", OperationalState.READY)),
            reasons=tuple(data.get("reasons", ())),
            process_id=int(pid),
        )

    @classmethod
    def from_json(cls, text: str) -> HostState:
        return cls.from_dict(json.loads(text))


def check_executable_path(target: str | Path) -> tuple[bool, str | None]:
    """Check whether a target is an executable dependency without executing it.

    Inspects only filesystem paths or PATH availability. Never runs the target binary.
    Returns (True, None) if executable.
    Returns (False, 'EXEC_NOT_FOUND') if nonexistent.
    Returns (False, 'EXEC_NOT_EXECUTABLE') if exists but not executable.
    """
    target_str = str(target).strip()
    if not target_str:
        return False, "EXEC_NOT_FOUND"

    has_dir = os.path.sep in target_str or (os.path.altsep and os.path.altsep in target_str)
    if has_dir:
        path = Path(target_str)
        if not path.exists():
            return False, "EXEC_NOT_FOUND"
        if path.is_dir():
            return False, "EXEC_NOT_EXECUTABLE"

        # Check executable permission or PATHEXT match
        if shutil.which(target_str) is not None:
            return True, None
        if os.name != "nt" and os.access(path, os.X_OK):
            return True, None
        return False, "EXEC_NOT_EXECUTABLE"
    else:
        resolved = shutil.which(target_str)
        if resolved is not None:
            return True, None
        return False, "EXEC_NOT_FOUND"


def check_state_dir(state_dir: Path) -> tuple[bool, str | None]:
    """Inspect state-storage capability without executing subprocesses or external tools."""
    try:
        if not state_dir.exists():
            state_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return False, ReasonCode.STATE_DIR_CREATE_FAILED

    if not state_dir.is_dir():
        return False, ReasonCode.STATE_DIR_NOT_DIRECTORY

    probe_path = state_dir / f".probe_write_{os.getpid()}_{time.time_ns()}.tmp"
    try:
        with open(probe_path, "w", encoding="utf-8") as f:
            f.write("probe\n")
        probe_path.unlink(missing_ok=True)
        return True, None
    except OSError:
        if probe_path.exists():
            try:
                probe_path.unlink()
            except OSError:
                pass
        return False, ReasonCode.STATE_DIR_NOT_WRITABLE


def persist_state(state: HostState | dict[str, Any], target_file: Path | str) -> Path:
    """Persist host state as strict UTF-8 JSON using atomic same-directory replacement.

    Guarantees readers never observe a partially written snapshot.
    """
    target = Path(target_file).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(state, HostState):
        content = state.to_json()
    else:
        content = HostState.from_dict(state).to_json()

    tmp_file = target.parent / f".{target.name}.tmp.{os.getpid()}.{time.time_ns()}"
    try:
        with open(tmp_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_file, target)
    except Exception:
        if tmp_file.exists():
            try:
                tmp_file.unlink()
            except OSError:
                pass
        raise

    return target


def load_state(target_file: Path | str) -> HostState:
    """Load host state from a file or directory."""
    path = Path(target_file).resolve()
    if path.is_dir():
        for candidate in ("host_state.json", "state.json"):
            if (path / candidate).exists():
                path = path / candidate
                break
        else:
            path = path / "host_state.json"

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return HostState.from_dict(data)


def _default_state_dir() -> Path:
    env_dir = os.environ.get("AIOS_NODE_STATE_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.home() / ".aios-node" / "state"


@dataclass
class HostConfig:
    """Configuration for AIOS-node host process."""

    state_dir: Path = field(default_factory=_default_state_dir)
    state_filename: str = "host_state.json"
    dependencies: dict[str, str | Path] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.state_dir, Path):
            self.state_dir = Path(self.state_dir)
        if not isinstance(self.dependencies, dict):
            self.dependencies = dict(self.dependencies)

    @property
    def state_file(self) -> Path:
        return self.state_dir / self.state_filename


class Host:
    """Persistent, non-polling host process lifecycle."""

    def __init__(self, config: HostConfig | None = None) -> None:
        self.config = config or HostConfig()
        self._stop_event = threading.Event()
        self._installed_signal_handlers = False

    def probe(self) -> HostState:
        """Derive operational readiness deterministically without external side effects."""
        reasons: list[str] = []

        if sys.version_info < (3, 11):
            reasons.append(ReasonCode.PYTHON_VERSION_INCOMPATIBLE)

        writable, dir_reason = check_state_dir(self.config.state_dir)
        if not writable and dir_reason:
            reasons.append(dir_reason)

        for name, target in sorted(self.config.dependencies.items()):
            ok, fail_type = check_executable_path(target)
            if not ok:
                if fail_type == "EXEC_NOT_FOUND":
                    reasons.append(ReasonCode.exec_not_found(name))
                elif fail_type == "EXEC_NOT_EXECUTABLE":
                    reasons.append(ReasonCode.exec_not_executable(name))
                else:
                    reasons.append(f"{fail_type}:{name}")

        sorted_reasons = tuple(sorted(reasons))
        op_state = OperationalState.READY if not sorted_reasons else OperationalState.DEGRADED
        return HostState(
            schema_version=SCHEMA_VERSION,
            operational_state=op_state,
            reasons=sorted_reasons,
            process_id=os.getpid(),
        )

    def persist(self, state: HostState | None = None) -> Path:
        """Atomically persist state snapshot."""
        state = state or self.probe()
        return persist_state(state, self.config.state_file)

    def request_stop(self) -> None:
        """Signal host idle loop to terminate gracefully."""
        self._stop_event.set()

    @property
    def is_stopped(self) -> bool:
        return self._stop_event.is_set()

    def install_signal_handlers(self) -> None:
        """Install SIGINT and SIGTERM handlers in the main thread."""
        if threading.current_thread() is threading.main_thread():
            def _signal_handler(signum: int, frame: Any) -> None:
                self.request_stop()

            for sig in (signal.SIGINT, signal.SIGTERM):
                try:
                    signal.signal(sig, _signal_handler)
                except (ValueError, AttributeError, OSError):
                    pass
            self._installed_signal_handlers = True

    def idle(self, timeout: float | None = None) -> bool:
        """Block without polling until stop is requested.

        Returns True if stop was signaled, False if timeout expired.
        """
        return self._stop_event.wait(timeout=timeout)

    def run(self, once: bool = False, timeout: float | None = None) -> HostState:
        """Execute host lifecycle: probe, persist state snapshot, and wait for stop."""
        state = self.probe()
        try:
            self.persist(state)
        except OSError:
            # If state directory cannot be written, state is already DEGRADED
            pass

        if once:
            return state

        self.install_signal_handlers()
        self.idle(timeout=timeout)
        return state
