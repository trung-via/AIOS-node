# N4 / NODE-003B — Android Cold-Boot Bootstrap Fallback

**Status:** ACTIVE DESIGN  
**Project:** AIOS-node  
**Target:** Xiaomi Mi 10 Pro / Android 10 MIUI-family host  
**Predecessor:** NODE-003 blocked at `HOST_BOOT_DELIVERY_BLOCKER`

## 1. Decision

Preserve the already-proven AIOS-node host and Termux runit service layers. Replace only the
Android cold-boot trigger with a tiny standalone Android helper application.

The helper owns exactly one lifecycle action:

```text
Android BOOT_COMPLETED
  -> fixed helper BootReceiver
  -> Termux exported RunCommandService
  -> fixed repository-owned Termux bootstrap script
  -> termux-services service-daemon
  -> already-reviewed runit aios-node service
  -> aios-node host READY
```

It is not an AIOS Runtime, dispatcher, scheduler, retry engine, or remote-control surface.

## 2. Why this is a materially different hypothesis

Termux:Boot v0.8.1 receives `BOOT_COMPLETED`, enumerates `~/.termux/boot`, schedules a
`JobScheduler` job for each file, and only then starts Termux execution from its JobService.
The physical Mi 10 Pro never produced the expected boot canary/evidence.

NODE-003B removes the Termux:Boot JobScheduler/file-enumeration layer. Its receiver performs one
fixed dispatch to Termux's exported `RunCommandService` instead.

A successful NODE-003B proof therefore isolates whether the Mi 10 Pro can cold-start a minimal
boot receiver plus the documented Termux external command bridge even though Termux:Boot did not
produce the required evidence.

## 3. Security boundary

The helper must be a normal standalone package with its own UID/signing identity.

It must **not**:

- use Termux's GitHub test signing key;
- request or share `android:sharedUserId="com.termux"`;
- access Termux private files directly;
- contain network permission;
- accept arbitrary command/path/argument input;
- export its boot receiver;
- expose a generic command API;
- invoke `aios`, `agy`, Codex, Git, model APIs, verification, repair, or publication;
- schedule retries, alarms, workers, polling, or replacement executions.

The only cross-app authority is the Termux-declared dangerous permission
`com.termux.permission.RUN_COMMAND`. The user must explicitly grant that permission to the helper.
Termux must also have `allow-external-apps=true` enabled for its documented external-command
surface. This broadening is accepted only for this bounded helper and must be documented clearly.

## 4. Fixed dispatch contract

The helper BootReceiver must dispatch exactly one explicit intent:

- component: `com.termux/com.termux.app.RunCommandService`;
- action: `com.termux.RUN_COMMAND`;
- command path: `/data/data/com.termux/files/home/.aios-node/bootstrap/start-services.sh`;
- runner/background mode: app-shell/background;
- arguments: empty;
- no caller-supplied values.

On Android O+, the helper must use `startForegroundService()` for the Termux RunCommandService;
older versions may use `startService()`.

The receiver records only host-local operational diagnostics in its own app preferences, such as
last boot-receiver timestamp and dispatch outcome. Those diagnostics are not canonical AIOS RESULT
or EVIDENCE.

## 5. Repository-owned Termux bootstrap script

`deploy/termux/bootstrap/start-services.sh` is the fixed command invoked by the helper after being
installed to:

`$HOME/.aios-node/bootstrap/start-services.sh`

The script may only:

- establish deterministic Termux `PREFIX`, `SVDIR`, and `LOGDIR`;
- write bounded host-local boot qualification markers;
- invoke `$PREFIX/bin/service-daemon start` exactly once.

It must not invoke AIOS, Executors, Git, network requests, verification, retries, loops, wake locks,
or publication.

## 6. One-time setup UI

The helper may contain one small launcher Activity whose only responsibilities are:

- report whether `com.termux.permission.RUN_COMMAND` is granted;
- request that permission when absent;
- show the last boot receiver / dispatch diagnostic values;
- explain that Termux `allow-external-apps=true` and Xiaomi Autostart / No-restrictions settings are
  required for qualification.

It must not expose a button that can execute arbitrary commands. A manual fixed bootstrap-test
button is not required for NODE-003B; physical cold-boot proof is the gate.

## 7. Build boundary

The Android helper should use only Android platform APIs and Java; no AndroidX, networking library,
agent SDK, model SDK, analytics, or background-work framework is needed.

A GitHub-hosted build workflow may create a disposable debug APK for physical qualification. It
must:

- use a GitHub-hosted runner only;
- require no repository secrets;
- build only this Android helper;
- upload the APK as a build artifact;
- never execute AIOS or attach a self-hosted node.

The debug APK is qualification packaging, not the final production signing decision. If the
fallback passes, stable signing/distribution can be addressed separately without changing the
boot authority contract.

## 8. Physical qualification gate

NODE-003B does not pass merely because source/static tests pass.

After the helper APK is built and installed on the Mi 10 Pro, qualification requires:

1. helper `RUN_COMMAND` permission granted;
2. Termux `allow-external-apps=true` configured;
3. helper Autostart enabled and battery policy unrestricted;
4. reviewed runit adapter and fixed bootstrap script deployed;
5. pre-reboot Android boot id and service state recorded;
6. physical Android reboot;
7. no manual Termux/service start before evidence collection;
8. helper diagnostic proves its BootReceiver ran in the new boot;
9. Termux bootstrap marker proves the fixed RunCommand dispatch executed;
10. `sv status aios-node` reports running;
11. host state is `READY` and PID agrees with runit;
12. no AIOS RUN or coding Executor was started by the lifecycle bootstrap.

Only then may N4 close.

## 9. Fail-closed behavior

If the helper does not receive boot, permission is absent, RunCommandService rejects execution, or
the service is not READY, NODE-003B remains BLOCKED/NOT PROVEN. Do not add retries or broaden
command authority as a convenience fix.
