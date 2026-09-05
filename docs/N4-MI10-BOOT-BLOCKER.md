# N4 — Mi 10 Pro Boot Delivery Blocker

**Status:** BLOCKED / NOT PROVEN  
**Project:** AIOS-node  
**Target host:** Xiaomi Mi 10 Pro / Android 10 MIUI-family host  
**Scope:** NODE-003 physical boot/restart conformance

## Summary

NODE-003 has proven the reviewed AIOS-node host and runit service behavior on the physical Mi 10 Pro, but N4 cannot yet close because the host-specific Android boot delivery mechanism has not executed Termux:Boot scripts after a real reboot.

This is not evidence of an AIOS-node Runtime defect and does not invalidate NODE-001 or NODE-002.

## Proven

The physical device proved all of the following:

- canonical AIOS-node source was synchronized to the phone;
- reviewed NODE-002 service adapter remained byte-identical to the reviewed implementation anchor;
- `aios-node` installed successfully in native Termux;
- `termux-services` / runit installed and resolved `SVDIR` correctly;
- `aios-node` service entered runit `run` state;
- host state reached `READY` with empty reasons;
- host-state `process_id` matched the runit-managed process PID;
- terminating the host PID with SIGTERM caused runit to start a new host PID automatically;
- the restarted host returned to `READY`;
- no AIOS RUN, coding Executor, retry, repair, or publication was started by service recovery;
- multiple physical Android reboots were proven by changing `/proc/sys/kernel/random/boot_id` values.

## Boot blocker evidence

Termux:Boot v0.8.1 was installed from the GitHub build family compatible with the GitHub Termux installation.

On-device configuration was verified:

- Termux:Boot launcher was opened;
- Termux:Boot Autostart was enabled;
- Termux Autostart was enabled;
- Termux:Boot battery policy was `No restrictions`;
- `~/.termux/boot/` existed;
- boot scripts were readable/executable;
- a minimal `00-boot-canary.sh` was installed that should write only a boot id and epoch to host-local evidence storage.

After real physical reboots:

- Android boot id changed, proving reboot actually occurred;
- the canary files were absent;
- the expected Termux:Boot marker and post-reboot evidence files were absent.

Therefore the N4 reboot gate is **not proven**.

## Diagnostic caveat

An attempted explicit shell `am broadcast` to `com.termux.boot/.BootReceiver` is not accepted as valid boot evidence because the Termux:Boot receiver is not an exported external API surface. Its result must not be used to classify the production boot path.

## Classification

Current classification:

`HOST_BOOT_DELIVERY_BLOCKER`

The blocker is below AIOS-node's reviewed host/service layer and above the Android/MIUI boot-event delivery boundary.

NODE-003 remains blocked rather than being marked PASS by inference.

## Architectural consequences

Do not:

- modify AIOS-renew;
- rerun NODE-001 or NODE-002;
- add AIOS execution retry logic;
- add a wake lock as a speculative fix;
- begin N5 while N4 reboot persistence is unproven;
- keep rebooting repeatedly without a changed boot mechanism or new measurable hypothesis.

## Fallback design requirements

The next boot mechanism must remain a thin lifecycle bootstrap only. It may start the already-reviewed local service supervisor, but must not gain TASK semantics, Executor authority, verification authority, retry authority, repair authority, or publication authority.

A fallback is acceptable only if it can produce deterministic physical evidence:

`new Android boot -> bootstrap invoked -> runit/service supervisor available -> aios-node host READY`

without a Human manually starting the service after reboot.

## Next step

Audit and select one Mi 10 Pro-specific boot bootstrap fallback. Preserve Termux runit as the service supervisor because that layer is already proven. Only the Android cold-boot trigger should change.
