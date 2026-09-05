# N4 — Persistent Host Plan

**Status:** ACTIVE  
**Project:** AIOS-node  
**Target host:** Xiaomi Mi 10 Pro / native Termux

## Goal

Turn the already-proven Mi 10 Pro execution substrate into a persistently available AIOS host without acquiring any authority owned by AIOS-renew.

N4 is host lifecycle only. It does not add remote wakeup, request dispatch, retries, repository synchronization, canonical verification, or executor control.

## Authority audit

N4 may own:
- AIOS-node process lifecycle;
- host-local operational readiness checks;
- Termux service supervision;
- boot restart of the AIOS-node host service;
- host operational state publication.

N4 must not own:
- TASK parsing or semantics;
- target repository admission/synchronization;
- mutation lease or source SHA binding;
- Executor invocation;
- model selection;
- Runtime verification/EVIDENCE;
- RESULT/FAILURE semantics;
- REVIEW/REMEDIATION/REPAIR;
- publication;
- retry of an admitted AIOS execution.

The runit supervisor may restart the AIOS-node host process itself. It must never be configured to restart an AIOS RUN or native coding Executor.

## Lean operational-state semantics

N4 defines the vocabulary but deliberately limits what the local host may assert.

- `READY`: AIOS-node host process is alive and required host-local dependencies pass bounded readiness checks.
- `DEGRADED`: host process is alive but one or more bounded host-local dependencies are unavailable.
- `BUSY`: reserved for a later bounded-request phase; N4 does not emit BUSY because it has no dispatch authority yet.
- `OFFLINE`: not self-authored by a dead process. It is inferred externally when the service/process is unreachable or absent.

These states are operational only and must never be mapped to AIOS engineering verdicts.

## Minimal host process

N4 introduces a small `aios-node host` process with no AI model and no repository mutation authority.

Required behavior:
1. perform bounded startup readiness checks only;
2. atomically persist one host-state snapshot in a host-local state directory;
3. remain alive while idle without polling or model calls;
4. handle normal termination cleanly;
5. never invoke `aios`, `agy`, Codex, Git mutation commands, project verification, or publication.

No periodic heartbeat is required in N4. Service liveness is provided by runit. This avoids unnecessary wakeups and power consumption.

## Readiness checks

Initial checks should remain host-local and bounded:
- Python runtime is usable;
- pinned/approved AIOS executable path exists and is executable when configured;
- Antigravity executable exists and is executable when configured;
- state directory is writable.

Readiness checks must not invoke a model, parse target TASKs, inspect target repository engineering state, or run target verification.

## N4 implementation sequence

### NODE-001 — Portable host core

Create the first production AIOS-node Python package and implement:
- host-state data model;
- atomic state-file persistence;
- bounded dependency probes;
- idle host process / clean signal termination;
- deterministic unit tests.

This task must be platform-neutral. No Termux path may leak into the core semantics.

### NODE-002 — Termux service adapter

Add a thin deployment adapter for `termux-services` / runit that starts only the AIOS-node host process.

The adapter must not launch AIOS RUNs or Executors.

### NODE-003 — Boot/restart conformance

Install and configure Termux:Boot from a signature-compatible source, start termux-services at boot, reboot the Mi 10 Pro, and prove:

```text
reboot
  -> Termux:Boot
  -> termux-services
  -> AIOS-node host service
  -> READY or deterministic DEGRADED
```

No canonical execution is required during the reboot proof.

## Android / Termux decisions

### termux-services

Use official `termux-services` (runit). It supervises only the Node host daemon.

### Termux:Boot signature provenance

The installed Termux app came from the GitHub build source. Termux plugins share signing requirements with the main Termux app, so Termux:Boot must come from a compatible GitHub signing source. Do not mix an F-Droid Termux:Boot APK with the current GitHub Termux installation.

### Wake lock

Do **not** make `termux-wake-lock` mandatory in the first N4 implementation.

The Mi 10 Pro is already configured with Android battery restrictions disabled for Termux. Continuous wake lock can increase battery consumption and heat. N4 should first test service persistence without it. Add wake lock only if reboot/screen-off evidence proves it necessary.

This follows the constitutional rule: evidence before expansion.

## Verification boundary

AIOS-node unit tests may verify Node host lifecycle/state behavior for the Node project itself.

On-device N4 qualification may verify:
- service starts;
- service restarts after its own process exits;
- state snapshot is READY/DEGRADED for bounded host reasons;
- service starts after reboot.

N4 must not re-run target-project canonical verification or reinterpret any prior AIOS RESULT.

## Gate

N4 passes when:
- the Node host core is implemented and canonically reviewed;
- the Termux runit service supervises the Node host process;
- reboot causes the service stack to restart automatically;
- the host reaches `READY` (or a deterministic, explained `DEGRADED` state if a host-local dependency is intentionally unavailable);
- no AIOS RUN or Executor is started by service restart;
- no duplicate authority with AIOS-renew is introduced.

## Non-goals

- no remote request ingestion;
- no GitHub Actions runner;
- no polling transport;
- no arbitrary shell API;
- no request dedupe yet;
- no automatic PRIMARY retry;
- no crash reconciliation yet;
- no Codex Android parity;
- no multi-node scheduler.