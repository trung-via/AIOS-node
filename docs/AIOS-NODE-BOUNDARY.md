# AIOS-node Boundary

**Status:** Canonical Architecture Boundary v1.0

This document answers one question:

> Does this capability belong in AIOS-renew or AIOS-node?

## Decision rule

```text
Does it determine WHAT should be built?
→ Brain / canonical TASK

Does it authorize repository mutation?
→ AIOS-renew

Does it invoke the production coding Executor?
→ AIOS-renew

Does it bind source SHA, scope, completion, or canonical verification?
→ AIOS-renew Runtime

Does it decide whether engineering work semantically passed?
→ Reviewer

Does it correct failed or defective engineering work?
→ REMEDIATION / REPAIR

Does it publish reviewed source?
→ Publication authority

Does it merely make a machine available, receive a bounded request,
start an approved AIOS operator command, survive reboot/network loss,
or report host health?
→ AIOS-node
```

If a proposed feature appears to own two of these branches at once, stop and perform an
architecture review before implementation.

## Non-overlap matrix

| Concern | AIOS-renew | AIOS-node |
| --- | --- | --- |
| TASK semantics | Owns | Forbidden |
| TASK parsing | Owns | Forbidden |
| Admission | Owns | Forbidden |
| Mutation lease | Owns | Forbidden |
| Git base SHA | Owns | Forbidden |
| PRIMARY synchronization | Owns | Forbidden |
| Executor dispatch | Owns | Forbidden |
| Model/executor mechanics | Adapter-owned | Forbidden |
| Runtime verification | Owns | Forbidden |
| EVIDENCE | Owns | Forbidden |
| RESULT / FAILURE | Owns | Observes only |
| REVIEW | External reviewer | Forbidden |
| REMEDIATION / REPAIR | Canonical correction | Forbidden |
| Publication | Separate authority | Forbidden |
| Device preflight | Does not own | Owns |
| Wakeup transport | Does not own | Owns |
| Delivery dedupe | Does not own | Owns |
| Host lifecycle | Does not own | Owns |
| Reboot recovery | Does not own | Owns operational restart |
| Host health | Does not own | Owns |
| Request reconciliation | Does not own | Observes canonical state only |

## Architectural prohibitions for v1

AIOS-node v1 must not:

1. invoke Codex or Antigravity directly for production TASK execution;
2. run `git pull`, reset, merge, rebase, stash, or checkout recovery on a target repository
   before an AIOS operation where AIOS-renew owns repository state transition;
3. repeat canonical target-project verification after AIOS Runtime;
4. parse executor/AIOS logs to invent PASS or failure semantics;
5. create REMEDIATION;
6. invoke REPAIR autonomously;
7. retry an admitted canonical RUN;
8. choose a different executor or model;
9. publish target product `main`;
10. copy TASK/RUN/RESULT into a second source-of-truth database;
11. add a Planner or LLM reasoning loop;
12. add a model router;
13. add a multi-node scheduler;
14. become a dependency of AIOS-renew.

Any future removal of one of these prohibitions requires explicit Human authorization and an
architecture-level TASK.

## Similar mechanisms that must remain semantically distinct

### Delivery dedupe vs mutation lease

Node dedupe answers: "Have I already delivered this request?"

AIOS mutation lease answers: "Who currently owns canonical repository mutation authority?"

They are not interchangeable.

### Host supervision vs Runtime timeout

Node supervision keeps the host/process environment available.

Runtime timeout governs canonical executor execution policy.

Node must not impose a shorter execution deadline that changes Runtime semantics.

### Host health vs engineering state

Node states such as READY/BUSY/DEGRADED/OFFLINE are operational.

AIOS RUN/RESULT/FAILURE and Reviewer verdicts are engineering state.

Never map one directly onto the other.

### Reconciliation vs REPAIR

Node reconciliation may inspect canonical state after crash or reboot.

It may not infer that a REPAIR should run, nor start one automatically.
