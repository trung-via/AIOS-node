# AIOS-node

AIOS-node is a portable, deterministic operational host for AIOS-renew.

Its job is to make compatible devices reliably available to canonical AIOS execution
without duplicating AIOS-renew authority.

## First target

Xiaomi Mi 10 Pro running Termux.

The architecture is intentionally device-neutral: Mi 10 Pro is the first node, not
the definition of the project.

## Authority boundary

AIOS-node may own:
- host/device preflight;
- process lifecycle and service startup;
- reboot restart;
- bounded request ingestion;
- delivery request identity and deduplication;
- one-shot invocation of approved AIOS operator surfaces;
- host/network health;
- operational observation;
- crash/reboot reconciliation by reading canonical AIOS state;
- host-specific compatibility adapters;
- minimum-privilege credential handling.

AIOS-node must not duplicate:
- TASK semantics or authoring;
- AIOS admission or mutation lease;
- executor dispatch mechanics;
- repository SHA/scope/completion gates;
- canonical verification or EVIDENCE;
- RESULT / FAILURE semantics;
- REVIEW;
- REMEDIATION / REPAIR;
- publication authority.

## Core relationship

```text
AIOS-node
    ↓ depends on
AIOS-renew

AIOS-renew
    X must not depend on
AIOS-node
```

Production coding-agent execution must always flow through AIOS-renew:

```text
remote bounded request
        ↓
AIOS-node
        ↓
approved AIOS operator command
        ↓
AIOS-renew
        ↓
selected executor
```

AIOS-node v1 contains no LLM, planner, reviewer, model router, or autonomous repair loop.

## Governance

Read in this order:

1. `docs/AIOS-NODE-CONSTITUTION.md`
2. `docs/AIOS-NODE-BOUNDARY.md`
3. `docs/CHATGPT_PROJECT_CONTRACT.md`
4. `docs/AIOS-NODE-ROADMAP.md`

## Current roadmap

```text
N0 Governance baseline
 ↓
N1 Mi 10 Pro host preflight
 ↓
N2 Pinned AIOS-renew compatibility
 ↓
N3 Disposable end-to-end execution proof
 ↓
N4 Persistent host
 ↓
N5 Bounded request contract
 ↓
N6 Private remote wakeup
 ↓
N7 Durable request identity
 ↓
N8 Crash/reboot reconciliation
 ↓
N9 Reliability / soak gate
 ↓
AIOS-node v1
```

Codex-on-Android, multi-node routing, automatic recovery, and generalized scheduling
are explicitly deferred until measured need exists.
