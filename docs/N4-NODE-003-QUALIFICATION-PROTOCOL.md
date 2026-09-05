# N4 / NODE-003 — Mi 10 Pro Persistence Qualification Protocol

**Status:** ACTIVE QUALIFICATION  
**Project:** AIOS-node  
**Target host:** Xiaomi Mi 10 Pro / native Termux  
**Canonical source baseline:** `442b4bbdb2e36c1ef72d3b4248f1762a4c669a4e`  
**Pinned AIOS-renew executable:** `$HOME/.venvs/aios-renew-5bdaa603/bin/aios`  
**Antigravity executable:** `$PREFIX/bin/agy`

## 1. Purpose

NODE-003 is the physical-host qualification step that closes N4 only after the actual Mi 10 Pro proves persistent host availability across runit restart and Android reboot.

This is deliberately **not** a normal coding-Executor implementation RUN. A Windows or headless coding Executor cannot truthfully attest that a physical Android device rebooted and restarted the service stack. The evidence boundary therefore remains on-device.

The qualification may mutate only host-local deployment/configuration state. It must not author target engineering state, launch a canonical AIOS RUN, invoke Antigravity/Codex, retry engineering work, or publish a target repository.

## 2. Preconditions

Before qualification:

- AIOS-node repository exists at `$HOME/AIOS-node` on the Mi 10 Pro.
- `origin/main` contains NODE-002 at `442b4bbdb2e36c1ef72d3b4248f1762a4c669a4e` or a later reviewed descendant that has not changed the N4 contract.
- pinned AIOS-renew remains available at `$HOME/.venvs/aios-renew-5bdaa603/bin/aios`.
- Antigravity remains available at `$PREFIX/bin/agy`.
- Termux is the native GitHub-source installation already qualified in N1/N2.
- Android battery restrictions for Termux remain disabled.
- Termux:Boot, when installed, must come from the same signing source as the installed Termux app. Do not mix GitHub and F-Droid signed Termux components.

No wake lock is required for the initial qualification.

## 3. Qualification authority boundary

Allowed host-local actions:

- synchronize the already-reviewed AIOS-node product source to the phone;
- install the AIOS-node package locally;
- install/configure `termux-services`;
- deploy the reviewed runit adapter;
- enable only the `aios-node` runit service;
- install/configure signature-compatible Termux:Boot;
- terminate the host process to prove runit restarts it;
- reboot the physical phone;
- read runit status and AIOS-node host-state snapshots;
- record bounded operational evidence.

Forbidden actions:

- `aios run`, `aios remediate`, `aios repair`, or publication;
- direct `agy`/Antigravity or Codex execution;
- automatic retry/recovery of canonical engineering work;
- target-project verification;
- arbitrary remote command ingestion;
- adding `termux-wake-lock` without measured suspension evidence.

## 4. Phase A — Deploy the reviewed host service

Run on the Mi 10 Pro in native Termux:

```sh
set -eu
cd "$HOME/AIOS-node"
git fetch origin main
git checkout main
git merge --ff-only origin/main

test "$(git rev-parse HEAD)" = "442b4bbdb2e36c1ef72d3b4248f1762a4c669a4e"

python -m pip install -e "$HOME/AIOS-node"

test "$(command -v aios-node)" = "$PREFIX/bin/aios-node"
test -x "$HOME/.venvs/aios-renew-5bdaa603/bin/aios"
test -x "$PREFIX/bin/agy"

pkg install -y termux-services

mkdir -p "$PREFIX/var/service/aios-node"
install -m 755 \
  "$HOME/AIOS-node/deploy/termux/services/aios-node/run" \
  "$PREFIX/var/service/aios-node/run"

test -x "$PREFIX/var/service/aios-node/run"
```

After installing `termux-services`, start its service daemon in the current Termux session by restarting the shell, or by sourcing the package-provided service startup profile when present. Then verify `SVDIR` resolves to `$PREFIX/var/service` before enabling the service.

Enable exactly the Node host service:

```sh
sv-enable aios-node
sleep 2
sv status aios-node
cat "$HOME/.aios-node/state/host_state.json"
```

Expected host-local state is `READY`, unless a bounded dependency is intentionally unavailable, in which case `DEGRADED` with an explicit reason is acceptable for diagnosis but does not close the N4 gate.

## 5. Phase B — Prove runit restarts only the host process

Capture the current host PID:

```sh
STATE="$HOME/.aios-node/state/host_state.json"
OLD_PID="$(python -c 'import json,os; print(json.load(open(os.path.expanduser("~/.aios-node/state/host_state.json"), encoding="utf-8"))["process_id"])')"
echo "OLD_PID=$OLD_PID"
kill -TERM "$OLD_PID"
sleep 2
NEW_PID="$(python -c 'import json,os; print(json.load(open(os.path.expanduser("~/.aios-node/state/host_state.json"), encoding="utf-8"))["process_id"])')"
echo "NEW_PID=$NEW_PID"
test "$NEW_PID" != "$OLD_PID"
sv status aios-node
cat "$STATE"
```

PASS requires:

- the original host process exits cleanly;
- runit starts a new `aios-node host` process with a different PID;
- the new process writes a valid `READY` snapshot;
- no AIOS RUN or coding Executor is started as a consequence of the restart.

This proves supervisor recovery is host-process recovery only.

## 6. Phase C — Configure Termux:Boot

Install Termux:Boot from the **same GitHub signing source** as the installed Termux app, then open the Termux:Boot app once so Android registers the boot receiver.

On Xiaomi/MIUI/HyperOS, enable app autostart/background-start permission for Termux:Boot and keep the already-approved battery settings for Termux. This is host lifecycle configuration, not AIOS engineering authority.

Create a deterministic boot script:

```sh
mkdir -p "$HOME/.termux/boot" "$HOME/.aios-node/boot-evidence"
cat > "$HOME/.termux/boot/10-start-aios-services.sh" <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
set -eu
PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
export PREFIX
export SVDIR="${SVDIR:-$PREFIX/var/service}"
export LOGDIR="${LOGDIR:-$PREFIX/var/log}"
mkdir -p "$HOME/.aios-node/boot-evidence"
date +%s > "$HOME/.aios-node/boot-evidence/termux_boot_invoked_epoch"
exec "$PREFIX/bin/service-daemon" start
EOF
chmod 700 "$HOME/.termux/boot/10-start-aios-services.sh"
```

The boot script intentionally contains no wake lock, no AIOS command, no Executor command, no Git operation, and no retry loop.

## 7. Phase D — Physical reboot proof

Before reboot, record:

```sh
rm -f "$HOME/.aios-node/boot-evidence/termux_boot_invoked_epoch"
rm -f "$HOME/.aios-node/boot-evidence/pre_reboot_state.json"
cp "$HOME/.aios-node/state/host_state.json" \
  "$HOME/.aios-node/boot-evidence/pre_reboot_state.json"
```

Then reboot the Mi 10 Pro normally.

After Android has completed boot, allow sufficient time for the boot receiver/service stack to start. When opening Termux for inspection, do **not** manually run `sv up`, `sv-enable`, `service-daemon start`, or `aios-node host` before collecting the evidence below.

Collect:

```sh
set -eu

echo "=== TERMUX_BOOT_MARKER ==="
cat "$HOME/.aios-node/boot-evidence/termux_boot_invoked_epoch"

echo "=== SERVICE_STATUS ==="
sv status aios-node

echo "=== HOST_STATE ==="
cat "$HOME/.aios-node/state/host_state.json"

echo "=== HOST_PID ==="
python -c 'import json,os; print(json.load(open(os.path.expanduser("~/.aios-node/state/host_state.json"), encoding="utf-8"))["process_id"])'
```

The boot marker exists only to establish that the Termux:Boot script executed. It is operational qualification evidence, not canonical AIOS RESULT/EVIDENCE.

## 8. NODE-003 PASS conditions

NODE-003 may be recorded PASS only when all of the following are observed on the physical Mi 10 Pro:

1. the reviewed NODE-002 service adapter is deployed unchanged from canonical product source;
2. `sv status aios-node` reports the service running;
3. the host reaches `READY` after normal service start;
4. terminating the host PID causes runit to restart the host with a new PID;
5. after a physical Android reboot, the Termux:Boot marker exists and the `aios-node` service is running without a manual service-start command;
6. the post-reboot host state is `READY`;
7. no service restart or boot action launches an AIOS RUN or coding Executor;
8. no wake lock is required for this first proof.

If the service is absent after reboot, NODE-003 remains **BLOCKED/NOT PROVEN** rather than inventing PASS. Diagnose Termux:Boot execution, Xiaomi autostart/background permissions, and service-daemon startup before considering any architecture expansion.

## 9. N4 closeout

After the physical evidence is supplied to Brain, record a canonical `N4-MI10-PERSISTENCE-REPORT.md` and advance the roadmap to N5 only if the N4 gate is actually proven.

Do not begin N5 remote request ingestion while NODE-003 is unproven.
