# N4 / NODE-003B — Android Cold-Boot Bootstrap Guide

**Status:** IMPLEMENTED (PENDING PHYSICAL QUALIFICATION)  
**Project:** AIOS-node  
**Target:** Xiaomi Mi 10 Pro / Android 10 (MIUI-family)  
**Predecessor:** NODE-003 (`HOST_BOOT_DELIVERY_BLOCKER`)  

---

## 1. Overview & Purpose

During NODE-003 physical qualification, the AIOS-node host core, runit service supervision, `READY` operational state, and runit-managed process restart were proven on the physical Mi 10 Pro. However, cold reboots did not trigger Termux:Boot scripts due to an on-device boot delivery blocker (`HOST_BOOT_DELIVERY_BLOCKER`, documented in [`docs/N4-MI10-BOOT-BLOCKER.md`](N4-MI10-BOOT-BLOCKER.md)). Termux:Boot's architecture relies on `JobScheduler` and directory enumeration after receiving `BOOT_COMPLETED`, which failed to deliver execution on this host.

NODE-003B provides a minimal, standalone Android cold-boot helper (`io.aios.node.bootstrap`) that bypasses Termux:Boot entirely. When Android broadcasts `BOOT_COMPLETED`, the helper performs exactly one explicit dispatch to Termux's documented, exported `RunCommandService` using action `com.termux.RUN_COMMAND` to invoke the fixed bootstrap script `deploy/termux/bootstrap/start-services.sh`.

```text
Android BOOT_COMPLETED
  -> io.aios.node.bootstrap.BootReceiver (non-exported)
  -> com.termux/com.termux.app.RunCommandService (com.termux.RUN_COMMAND)
  -> ~/.aios-node/bootstrap/start-services.sh
  -> $PREFIX/bin/service-daemon start
  -> runit /var/service/aios-node
  -> aios-node host process (READY)
```

---

## 2. Security Boundary & Authority Audit

The helper is designed under strict least-privilege principles:

1. **Standalone Identity**:
   - Package name: `io.aios.node.bootstrap`
   - Independent Android UID; no `android:sharedUserId` is declared.
   - Does not share Termux's signing keys or private files.

2. **Minimum Permissions**:
   - `android.permission.RECEIVE_BOOT_COMPLETED`: To receive standard system boot broadcasts.
   - `com.termux.permission.RUN_COMMAND`: Termux-declared dangerous permission required to invoke `RunCommandService`.
   - **Forbidden permissions**: Manifest requests no `INTERNET`, storage, wake-lock, accessibility, device-admin, VPN, or root permissions.

3. **Fixed Dispatch Contract**:
   - Dispatches strictly to `com.termux/com.termux.app.RunCommandService`.
   - Action is strictly `com.termux.RUN_COMMAND`.
   - Command path is a compile-time constant:
     `/data/data/com.termux/files/home/.aios-node/bootstrap/start-services.sh`
   - Command arguments are strictly empty (`new String[0]`).
   - Runner mode is `app-shell` in the background (`RUN_COMMAND_BACKGROUND=true`).
   - No dynamic Intent extras, UI fields, files, network payloads, or external inputs can alter the target component, action, path, or arguments.

4. **Security Implication of Termux `allow-external-apps=true`**:
   - Termux external-command policy requires setting `allow-external-apps=true` in `~/.termux/termux.properties`.
   - **Critical Security Note**: Enabling `allow-external-apps=true` allows any third-party app granted `com.termux.permission.RUN_COMMAND` to execute commands in Termux's environment.
   - **Requirement**: During qualification and operation, `com.termux.permission.RUN_COMMAND` must be granted **ONLY** to this bounded helper (`io.aios.node.bootstrap`). No untrusted third-party application may be granted this permission.

5. **No Duplicate Execution Authority**:
   - The helper and the bootstrap script contain no AIOS Runtime, Planner, Brain, Executor, model, Git, network, verification, retry, loop, alarm, worker, or publication authority.
   - Operational diagnostics stored in the helper's `SharedPreferences` (last boot received timestamp, last dispatch time, dispatch result) are bounded local diagnostics only and never represent canonical AIOS engineering state.

---

## 3. Artifact Limitations

The debug APK produced by `.github/workflows/build-android-bootstrap.yml` is a **disposable qualification artifact** designed for physical testing on the Mi 10 Pro test node.
- It is built using GitHub-hosted runners (`ubuntu-latest`) without repository secrets.
- It is signed with the standard Android debug key.
- It does not represent a final production signing or distribution model. Stable signing and distribution remain deferred until physical cold-boot evidence is proven.

---

## 4. Installation & Deployment Guide

### Step 1: Deploy the bootstrap script in Termux

Copy `deploy/termux/bootstrap/start-services.sh` to the required destination:

```bash
mkdir -p "$HOME/.aios-node/bootstrap"
cp deploy/termux/bootstrap/start-services.sh "$HOME/.aios-node/bootstrap/start-services.sh"
chmod 700 "$HOME/.aios-node/bootstrap/start-services.sh"
```

Verify that native Termux shell path `#!/data/data/com.termux/files/usr/bin/sh` is present and line endings are LF.

### Step 2: Configure Termux external apps policy

Ensure `~/.termux/termux.properties` has `allow-external-apps` enabled:

```bash
mkdir -p "$HOME/.termux"
if ! grep -q "^allow-external-apps=true" "$HOME/.termux/termux.properties" 2>/dev/null; then
    echo "allow-external-apps=true" >> "$HOME/.termux/termux.properties"
fi
```

Restart Termux or run `termux-reload-settings` to apply.

### Step 3: Install the qualification APK

Download `app-debug.apk` from the GitHub Actions run artifact `aios-boot-bootstrap-debug-apk` and install it:

```bash
adb install -r app-debug.apk
```

### Step 4: Grant `com.termux.permission.RUN_COMMAND`

Grant the dangerous permission via the helper's `MainActivity` UI by tapping "Request RUN_COMMAND Permission", or via `adb`:

```bash
adb shell pm grant io.aios.node.bootstrap com.termux.permission.RUN_COMMAND
```

Verify in `MainActivity` that the status reports `Status: GRANTED`.

### Step 5: Configure Xiaomi MIUI background settings

On the Mi 10 Pro (MIUI 12 / Android 10):
1. **Autostart**:
   - Go to Settings > Apps > Manage apps > **AIOS Boot Bootstrap** > Enable **Autostart**.
   - Go to Settings > Apps > Manage apps > **Termux** > Enable **Autostart**.
2. **Battery saver**:
   - Go to Settings > Apps > Manage apps > **AIOS Boot Bootstrap** > Battery saver > Select **No restrictions**.
   - Go to Settings > Apps > Manage apps > **Termux** > Battery saver > Select **No restrictions**.

---

## 5. Physical Cold-Boot Qualification Protocol

> **IMPORTANT**: Completion of the NODE-003B source code does **NOT** mark N4 as PASS.  
> Physical cold-boot evidence on the Mi 10 Pro remains an independent, mandatory qualification requirement.

### The 12-Point Qualification Gate

1. **Permission Verified**: Helper `MainActivity` confirms `com.termux.permission.RUN_COMMAND` is granted.
2. **Termux Policy Configured**: `allow-external-apps=true` confirmed in `~/.termux/termux.properties`.
3. **Autostart & Battery Policy**: Helper and Termux configured with Autostart enabled and "No restrictions".
4. **Adapter & Bootstrap Deployed**: Reviewed `aios-node` runit service and `~/.aios-node/bootstrap/start-services.sh` deployed.
5. **Pre-reboot State Recorded**: Pre-reboot `/proc/sys/kernel/random/boot_id` and service status recorded.
6. **Physical Reboot Executed**: Device reboot initiated (`adb reboot` or physical power cycle).
7. **No Manual Intervention**: Device reaches lockscreen / boot complete without manual Termux or service start.
8. **Helper Dispatch Proven**: Helper diagnostics in `MainActivity` or SharedPreferences prove `BootReceiver` ran during the new boot session and dispatched successfully (`DISPATCHED`).
9. **Bootstrap Script Marker Proven**: `$HOME/.aios-node/bootstrap/markers/last_boot.marker` exists with the new boot ID.
10. **Service Supervisor Running**: `sv status aios-node` reports `run: aios-node: (pid ...)`.
11. **Host State READY**: `$HOME/.aios-node/state/host_state.json` reports `operational_state: READY` with matching PID.
12. **No Autonomous Work Started**: No AIOS RUN, coding Executor (`agy`), git mutation, or publication was invoked.

Only when all 12 points are verified with real host artifacts may N4 close.

---

## 6. Fail-Closed Principles

If the physical reboot fails to start the service:
- Inspect `MainActivity` diagnostics to check whether `BootReceiver` was invoked.
- If `BootReceiver` was not invoked, Android system did not deliver `BOOT_COMPLETED` (MIUI autostart restriction).
- If `BootReceiver` ran but dispatch failed, check `last_error` (permission denied or service rejected).
- Do **NOT** add speculative retry loops, wake locks, background workers, or alarms. The architecture demands clean, deterministic qualification evidence.
