# N4 / NODE-003B — Physical Cold-Boot Qualification Failure

**Status:** BLOCKED / PHYSICAL GATE FAILED  
**Project:** AIOS-node  
**Target:** Xiaomi Mi 10 Pro / Android 10 MIUI-family host  
**Source implementation:** PASS / published at `f4db260e6c31b0ecc120aca0c599dce4c1853ee7`

## Summary

NODE-003B source implementation passed review and publication, but the physical Mi 10 Pro cold-boot qualification failed at Android boot-event delivery.

The standalone helper was intentionally designed to bypass Termux:Boot's JobScheduler/file-enumeration path. Despite that materially different implementation, the helper's non-exported `BOOT_COMPLETED` receiver did not run after a proven physical reboot.

N4 therefore remains **NOT PASS**.

## Qualification setup proven before reboot

The device state before reboot proved:

- repository synchronized to published source `f4db260e6c31b0ecc120aca0c599dce4c1853ee7`;
- `deploy/termux/bootstrap/start-services.sh` deployed byte-identically to `~/.aios-node/bootstrap/start-services.sh` and executable;
- `allow-external-apps=true` configured for Termux;
- helper `com.termux.permission.RUN_COMMAND` status was `GRANTED`;
- helper Autostart / battery prerequisites were configured for qualification;
- Termux:Boot active boot directory was empty;
- the Termux login service hook was moved aside, preventing shell-open auto-start from contaminating post-reboot evidence;
- bootstrap marker was removed before reboot;
- pre-reboot boot id was `1ee6b95b-6b4c-46e4-9c5f-2f4287b1b49e`;
- pre-reboot `aios-node` service was running and host state was `READY` with PID `6419`.

## Post-reboot evidence

After the physical reboot, before any service start was allowed to contaminate evidence:

- current boot id was `4df1a99a-813e-442b-9656-daebb2d270fb`, proving a new Android boot session;
- AIOS Boot Bootstrap UI still reported:
  - `Last BOOT_COMPLETED received: none`;
  - `Last RunCommand dispatch: none`;
  - `Last dispatch result: none`;
  - `Last error: none`;
- `~/.aios-node/bootstrap/markers/last_boot.marker` was absent;
- explicit `SVDIR=$PREFIX/var/service` service inspection reported `aios-node: runsv not running`;
- old pre-reboot PID `6419` no longer existed;
- no `runsvdir`, `runsv`, `service-daemon`, or `aios-node host` process was present;
- log inspection produced no `AiosBootReceiver`, helper package boot, or relevant `BOOT_COMPLETED` execution evidence.

The persisted `host_state.json` still contained pre-reboot `READY` / PID `6419`; this is stale persisted state and is explicitly **not** accepted as proof of a live host after reboot.

## Classification

`HOST_BOOT_BROADCAST_DELIVERY_BLOCKER`

The failure boundary is now narrower than NODE-003:

```text
Android physical reboot proven
  -> BOOT_COMPLETED not observed by standalone helper
  -> no Termux RunCommand dispatch
  -> no bootstrap marker
  -> no service-daemon / runit host process
```

This means both tested application-level boot paths failed on this Mi 10 Pro:

1. Termux:Boot v0.8.1 boot receiver / JobScheduler path;
2. standalone AIOS Boot Bootstrap direct receiver / Termux RunCommandService path.

The common unresolved boundary is Android/MIUI cold-boot broadcast delivery to third-party application receivers, not AIOS-node host logic, runit, AIOS-renew, or executor behavior.

## Architectural consequences

Do not:

- mark NODE-003B physical qualification PASS;
- mark N4 PASS;
- begin N5;
- modify AIOS-renew for this blocker;
- rerun NODE-001 or NODE-002;
- add retry loops, WorkManager, JobScheduler, alarms, wake locks, polling, or duplicate boot receivers to the helper as speculative fixes;
- use stale `host_state.json` as live-process evidence;
- perform repeated reboots without changing the boot authority mechanism.

## Next decision boundary

The next mechanism must be outside the already-failed third-party `BOOT_COMPLETED` application-receiver path while preserving the proven runit/service layer.

Before selecting that mechanism, determine host privilege capability (for example whether a root/system boot hook is actually available on this device). If no privileged boot hook is available, the project must explicitly choose between a weaker post-unlock/user-launch availability model or a different host device rather than silently weakening N4's reboot gate.
