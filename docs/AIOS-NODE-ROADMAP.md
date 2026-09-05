# AIOS-node Roadmap

**Status:** ACTIVE ROADMAP  
**Project:** AIOS-node  
**First target:** Xiaomi Mi 10 Pro / Termux

## North Star

```text
Verified Useful Work / (Time + Tokens + Human Effort)
```

AIOS-node is intentionally a deterministic host/transport layer. It must not grow into a
second AIOS Runtime or orchestration authority.

## Current state

```text
N0 Governance Baseline             DONE
N1 Mi 10 Pro Host Preflight        DONE
N2 Pinned AIOS-renew Compatibility DONE
N3 Disposable End-to-End Proof     DONE
N4 Persistent Host                 ACTIVE
```

N1 canonical report: [`N1-MI10-PREFLIGHT-REPORT.md`](N1-MI10-PREFLIGHT-REPORT.md)

N2 canonical compatibility target: [`N2-AIOS-RENEW-PIN.md`](N2-AIOS-RENEW-PIN.md)

N2 canonical report: [`N2-MI10-COMPATIBILITY-REPORT.md`](N2-MI10-COMPATIBILITY-REPORT.md)

N3 execution plan: [`N3-DISPOSABLE-E2E-PLAN.md`](N3-DISPOSABLE-E2E-PLAN.md)

N3 canonical report: [`N3-MI10-E2E-REPORT.md`](N3-MI10-E2E-REPORT.md)

N4 active plan: [`N4-PERSISTENT-HOST-PLAN.md`](N4-PERSISTENT-HOST-PLAN.md)

N4 active qualification: [`N4-NODE-003-QUALIFICATION-PROTOCOL.md`](N4-NODE-003-QUALIFICATION-PROTOCOL.md).

## Required sequence

### N0 — Governance Baseline — DONE

Deliver:
- `AIOS-NODE-CONSTITUTION.md`
- `AIOS-NODE-BOUNDARY.md`
- `CHATGPT_PROJECT_CONTRACT.md`
- this roadmap
- README

Gate:
- project authority is explicit before production code exists;
- one-way dependency on AIOS-renew is fixed;
- architectural prohibitions are recorded.

Result: PASS.

### N1 — Mi 10 Pro Host Preflight — DONE

Goal:
Prove the Mi 10 Pro / Termux host has the minimum mechanics required to host AIOS without
changing AIOS-renew semantics.

Inspect/measure:
- ARM64 / aarch64 architecture;
- Python >= 3.11;
- Git;
- POSIX shell resolution;
- strict UTF-8 behavior;
- filesystem read/write/rename behavior in Termux private storage;
- `fcntl.flock()` support;
- subprocess execution;
- network/DNS/TLS;
- available disk/RAM;
- `agy` binary availability and basic non-production invocation;
- background/battery constraints relevant to later persistence.

Non-goals:
- no AIOS RUN yet;
- no GitHub Actions runner;
- no persistent daemon;
- no automatic fixes to AIOS-renew.

Gate:
Produce a deterministic preflight report with PASS/FAIL/UNKNOWN host capabilities.

Result: PASS. See [`N1-MI10-PREFLIGHT-REPORT.md`](N1-MI10-PREFLIGHT-REPORT.md).

Observed compatibility concern deferred to N2: native Termux resolves `sh` under the Termux
prefix rather than `/bin/sh`. This is not yet a proven AIOS-renew defect; N2 must reproduce
any incompatibility against the exact pinned upstream runtime before proposing a kernel change.

### N2 — Pinned AIOS-renew Compatibility — DONE

Goal:
Install and bind AIOS-node development to an explicit AIOS-renew commit/version and prove
the approved operator surface can be invoked on the Mi 10 Pro.

Requirements:
- explicit upstream pin;
- no assumption that AIOS current main equals Node-compatible runtime;
- no target-repository mutation outside approved AIOS surfaces;
- production Antigravity installation must be pinned and provenance-aware;
- compatibility proof must use a disposable repository;
- any portability failure must be reproduced against the pinned runtime before proposing an upstream change.

Pinned target:
`5bdaa603924ac6104ed28413ad91a4cc1b7f6d0b`.

Gate:
`aios` is callable on the Mi 10 Pro against a disposable repository without architecture drift.

Result: PASS. See [`N2-MI10-COMPATIBILITY-REPORT.md`](N2-MI10-COMPATIBILITY-REPORT.md).

### N3 — Disposable End-to-End Execution Proof — DONE

Goal:
Prove one canonical AIOS execution on a disposable smoke repository using Antigravity through
AIOS-renew.

Required flow:
```text
bounded local request
  ↓
AIOS-node bootstrap surface
  ↓
approved `aios ...` operator command
  ↓
AIOS-renew
  ↓
Antigravity
  ↓
Runtime verification
  ↓
canonical RESULT / FAILURE
```

Hard constraints:
- Node does not invoke `agy` directly for production execution;
- Node does not run canonical verification separately;
- Node does not publish or repair.

Gate:
A complete attributable execution exists with no duplicate authority.

Result: PASS via `RUN-N3-SMOKE-001`. See [`N3-MI10-E2E-REPORT.md`](N3-MI10-E2E-REPORT.md).

### N4 — Persistent Host — ACTIVE

Goal:
Keep AIOS-node available across normal Android lifecycle events.

Target mechanisms:
- portable host core;
- Termux native service supervision;
- boot restart;
- bounded host state vocabulary: READY / BUSY / DEGRADED / OFFLINE.

Semantic refinement:
- N4 core locally emits READY or DEGRADED only;
- BUSY is reserved for later bounded dispatch;
- OFFLINE is inferred externally rather than self-authored by a dead process.

Implementation / qualification sequence:
- `NODE-001` — portable host core — PASS / published at `aff7f49f546cb5a9f777ceeb4d58470e8fbbcecb`;
- `NODE-002` — thin Termux runit service adapter — PASS / published at `442b4bbdb2e36c1ef72d3b4248f1762a4c669a4e`;
- `NODE-003` — physical Mi 10 Pro boot/restart conformance — ACTIVE.

`NODE-003` is an on-device qualification boundary, not a coding-Executor implementation RUN. A coding Executor cannot truthfully attest a physical Android reboot. PASS requires direct device evidence under [`N4-NODE-003-QUALIFICATION-PROTOCOL.md`](N4-NODE-003-QUALIFICATION-PROTOCOL.md).

Non-goals:
- no remote wakeup yet;
- no autonomous execution retry;
- no AIOS RUN supervision or restart;
- no mandatory wake lock without measured need.

Gate:
reboot → service restart → READY (or deterministic host-local DEGRADED), with no invented engineering state and no AIOS RUN started by service recovery.

Active plan: [`N4-PERSISTENT-HOST-PLAN.md`](N4-PERSISTENT-HOST-PLAN.md).

### N5 — Bounded Request Contract

Goal:
Define the only remote data AIOS-node is permitted to accept.

V1 request payload should contain bounded identifiers such as:
- request_id;
- repository_id / configured repository alias;
- operation;
- task_id;
- selected executor;
- optional finding_id or failed_run_id only when that operation is later explicitly enabled.

Forbidden:
- arbitrary shell;
- arbitrary command text;
- executable scripts supplied by caller.

Initial enabled operation:
- PRIMARY only, unless later evidence justifies expansion.

Gate:
invalid/unrecognized/unbounded requests fail before AIOS invocation.

### N6 — Private Remote Wakeup

Goal:
Allow a remote Human/Brain control-plane event to wake one Mi 10 Pro node.

Architecture:
```text
private control plane
  ↓
bounded request
  ↓
Mi 10 Pro
  ↓
AIOS-node
```

Security:
- do not attach persistent self-hosted execution to an untrusted public workflow surface;
- minimum credentials;
- control-plane credentials separated from publication authority.

Gate:
one authorized remote request produces at most one approved AIOS invocation.

### N7 — Durable Request Identity

Goal:
Make duplicate transport events deterministic no-ops without pretending to own AIOS mutation leases.

Persistent operational journal:
- request_id;
- received state;
- target repo alias;
- operation;
- task id;
- selected executor;
- associated process/run observation when known.

Gate:
same request delivered twice does not start two canonical executions.

### N8 — Crash / Reboot Reconciliation

Goal:
After host/process loss, reconnect operational request identity to canonical AIOS state.

Allowed:
- inspect canonical repository state;
- report known terminal state;
- report active/uncertain/recovery-required state.

Forbidden:
- automatic replacement PRIMARY;
- automatic REMEDIATION;
- automatic REPAIR;
- automatic publication.

Gate:
crash/reboot never causes silent duplicate mutation.

### N9 — Reliability / Soak Gate

Required scenarios:
- screen off;
- reboot;
- Wi-Fi → mobile data;
- mobile data → Wi-Fi;
- network loss and recovery;
- Android kills/suspends service;
- remote duplicate event;
- long Antigravity execution;
- host restart during execution;
- stale request;
- low storage / low battery observation where practical.

Completion criterion:
Mi 10 Pro can reliably receive an authorized bounded request, invoke exactly one canonical
AIOS execution through the approved operator surface, survive normal mobile-host lifecycle
events without duplicating execution, and expose enough operational state for deterministic
reconciliation.

## Deferred until after v1

- Codex-on-Android parity;
- laptop host parity hardening;
- multi-node routing;
- capability-based scheduler;
- autonomous repair/recovery;
- generalized agent orchestration.

None of these block AIOS-node v1.
