# N4 — Termux Runit Service Adapter

**Status:** ACTIVE SPECIFICATION
**Task:** NODE-002
**Target host:** Xiaomi Mi 10 Pro / native Termux
**Service supervisor:** `termux-services` (runit)

## 1. Overview and Goal

The purpose of the Termux runit service adapter is to provide a thin, repository-owned deployment definition that allows `termux-services` / runit to supervise the `aios-node host` process persistently across mobile host lifecycle events.

This adapter preserves the strict authority boundary established by `AIOS-NODE-CONSTITUTION.md`, `AIOS-NODE-BOUNDARY.md`, and proven during N3:
- AIOS-node is a host lifecycle and delivery substrate; it is not an engineering execution or orchestration authority.
- The adapter supervises only the local `aios-node host` process.
- It does not launch, supervise, restart, retry, or recover canonical AIOS RUNs or coding Executors.

## 2. Deployment Destination

Under native Termux with the official `termux-services` package installed, user-level runit service directories reside under `$PREFIX/var/service/`.

The canonical deployment destination for this service is:

```text
$PREFIX/var/service/aios-node
```

The service directory structure deployed on the target device consists of the executable run script:

```text
$PREFIX/var/service/aios-node/run
```

In this repository, the source template is maintained at:

```text
deploy/termux/services/aios-node/run
```

The committed run file possesses executable Git mode (`100755`) and uses POSIX line endings (`LF`).

## 3. Configuration Boundary and Environment Overrides

The adapter exposes deterministic environment-overridable paths for all host dependencies while providing proven default fallbacks for the Xiaomi Mi 10 Pro layout.

### Overridable Variables

| Variable | Default Value | Role / Purpose |
| --- | --- | --- |
| `PREFIX` | `/data/data/com.termux/files/usr` | Native Termux user prefix directory |
| `HOME` | `/data/data/com.termux/files/home` | Native Termux home directory |
| `AIOS_NODE_BIN` | `$PREFIX/bin/aios-node` | Path to the installed `aios-node` CLI executable |
| `AIOS_NODE_STATE_DIR` | `$HOME/.aios-node/state` | Directory for atomic operational state snapshots |
| `AIOS_NODE_AIOS_BIN` | `${AIOS_BIN:-$HOME/.venvs/aios-renew-5bdaa603/bin/aios}` | Pinned AIOS-renew CLI executable path |
| `AIOS_NODE_ANTIGRAVITY_BIN` | `${ANTIGRAVITY_BIN:-${AGY_BIN:-$PREFIX/bin/agy}}` | Antigravity CLI executable path |

### Bounded Readiness Inputs vs Execution

The paths configured via `AIOS_NODE_AIOS_BIN` and `AIOS_NODE_ANTIGRAVITY_BIN` are passed exclusively as command-line arguments (`--aios-bin` and `--antigravity-bin`) to `aios-node host`.

They are **bounded readiness-probe inputs only**:
- The service adapter never executes `aios` or `agy`.
- The `aios-node host` process checks only filesystem presence and executable permissions via `check_executable_path()`.
- Neither binary is executed during startup, probing, or idle lifecycle.

### Isolation of Platform Paths

The adapter is a thin deployment wrapper. Termux-specific directory paths (`/data/data/com.termux/...`) are strictly isolated to `deploy/termux/` and documentation. No Termux-specific paths, environment variables, or platform policies may be moved into `src/aios_node/`. The host core remains completely platform-neutral.

## 4. Process Model and Supervision Semantics

The runit `run` script implements the following execution model:

```sh
#!/data/data/com.termux/files/usr/bin/sh
exec 2>&1

PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
HOME="${HOME:-/data/data/com.termux/files/home}"

AIOS_NODE_BIN="${AIOS_NODE_BIN:-$PREFIX/bin/aios-node}"
AIOS_NODE_STATE_DIR="${AIOS_NODE_STATE_DIR:-$HOME/.aios-node/state}"
AIOS_NODE_AIOS_BIN="${AIOS_NODE_AIOS_BIN:-${AIOS_BIN:-$HOME/.venvs/aios-renew-5bdaa603/bin/aios}}"
AIOS_NODE_ANTIGRAVITY_BIN="${AIOS_NODE_ANTIGRAVITY_BIN:-${ANTIGRAVITY_BIN:-${AGY_BIN:-$PREFIX/bin/agy}}}"

exec "$AIOS_NODE_BIN" host \
    --state-dir "$AIOS_NODE_STATE_DIR" \
    --aios-bin "$AIOS_NODE_AIOS_BIN" \
    --antigravity-bin "$AIOS_NODE_ANTIGRAVITY_BIN"
```

Key characteristics:
1. **Native Termux shell:** Uses `#!/data/data/com.termux/files/usr/bin/sh`.
2. **Process replacement (`exec`):** The script executes `aios-node host` via `exec`, ensuring the Python host process replaces the shell and runs with the exact PID supervised by runit.
3. **No internal loops or child supervisors:** The run script contains no `while`, `until`, `for`, `sleep`, or retry logic. Runit itself is the supervisor.
4. **Standard error redirection:** `exec 2>&1` redirects standard error to standard output for capture by the runit logging facility.
5. **Clean termination:** Runit stops services by sending `SIGTERM`. The host process catches `SIGTERM` and `SIGINT`, unblocks its idle wait, and exits cleanly with status 0.

## 5. Host Availability vs Engineering Execution

**Fundamental Rule:**
Runit supervises **only host availability**, never engineering execution.

- Explicit rule: runit may restart the AIOS-node host process after host-process exit but must never be treated as authority to restart canonical AIOS work.
- Runit must **never** be treated as authority to retry a canonical RUN, re-execute tasks, or invoke Executors.
- The `aios-node host` process is non-polling and passive: when started or restarted by runit, it evaluates host-local readiness, atomically records `READY` or `DEGRADED` to `host_state.json`, and enters an idle wait. It never starts, resumes, or retries AIOS operations autonomously.

## 6. NODE-003 Activation Step

In accordance with minimal-privilege and step-by-step verification, service activation is explicitly deferred to **NODE-003**:

- **No self-activation:** The service run file must not enable or disable itself.
- **Prohibited in NODE-002:** Calling `sv`, `sv-enable`, `sv-disable`, `sv up`, `sv down`, Termux:Boot setup, or `termux-wake-lock`.
- **Activation in NODE-003:** Once on-device qualification begins in NODE-003:
  1. The service folder is deployed to `$PREFIX/var/service/aios-node`.
  2. The service is enabled via `sv-enable aios-node`.
  3. Boot persistence is configured via Termux:Boot (`~/.termux/boot/start-services`).
  4. Device reboot is tested to confirm that `aios-node host` starts automatically and records a valid state snapshot without any AIOS execution trigger.

## 7. Wake Lock Policy

In alignment with the constitutional principle of *evidence before expansion*, `termux-wake-lock` is omitted from this service definition. Android battery restrictions have already been disabled for Termux on the Mi 10 Pro. Continuous wake lock will be considered only if on-device qualification in NODE-003 or N9 reveals measurable suspension during necessary operational windows.
