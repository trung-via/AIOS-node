# ChatGPT Project Contract — AIOS-node

**Status:** Durable Project Governance  
**Scope:** ChatGPT Brain behavior for the AIOS-node project

## 1. Project Identity

AIOS-node is a portable operational host for AIOS-renew.

Its purpose is to make compatible devices reliably available to canonical AIOS execution
while preserving AIOS-renew as the engineering execution authority.

The first target host is Xiaomi Mi 10 Pro running Termux. The architecture must not assume
that future nodes are Android devices.

## 2. Upstream Boundary

AIOS-node integrates with an explicitly pinned or otherwise explicitly compatible
AIOS-renew version.

AIOS-renew owns canonical engineering execution semantics.

AIOS-node must not duplicate or reinterpret:
- TASK semantics;
- admission;
- Dispatcher authority;
- mutation leases;
- repository SHA/scope gates;
- Executor invocation mechanics;
- canonical verification;
- EVIDENCE;
- RESULT or FAILURE;
- REVIEW;
- REMEDIATION;
- REPAIR;
- publication authority.

If an actual AIOS-renew portability defect is discovered, record the evidence and address
it through a separate canonical AIOS-renew TASK rather than implementing competing behavior
inside AIOS-node.

## 3. AIOS-node Responsibilities

AIOS-node may own:
- host/device preflight;
- repository location mapping;
- process lifecycle;
- service startup;
- reboot restart;
- bounded remote request ingestion;
- delivery-request identity and deduplication;
- one-shot invocation of approved AIOS operator commands;
- operational process observation;
- network/device health;
- crash/reboot reconciliation by reading canonical AIOS state;
- host-specific compatibility adapters;
- minimum-privilege credential handling;
- operational telemetry.

These are operational responsibilities, not engineering-semantic authority.

## 4. Forbidden Responsibilities

AIOS-node must not:
- author or revise target TASK semantics;
- directly run production coding Executors instead of AIOS-renew;
- select another Executor or model;
- automatically retry an admitted execution;
- run canonical target-project verification independently;
- construct canonical evidence;
- judge PASS, CHANGES_REQUIRED, or BLOCKED;
- automatically create or execute REMEDIATION or REPAIR;
- synchronize target Git state where AIOS-renew already owns synchronization;
- publish target product main;
- convert host logs into canonical engineering truth;
- implement an alternative AIOS Runtime.

## 5. Brain Responsibilities

ChatGPT Brain owns WHAT and WHY for AIOS-node itself:
- operational goals;
- host boundary;
- security requirements;
- portability requirements;
- request contract;
- lifecycle semantics;
- task scope;
- acceptance criteria;
- Node roadmap;
- semantic review of AIOS-node implementation.

Brain must audit every proposed feature for overlap with AIOS-renew before authoring a Node TASK.

## 6. Implementation Authority

Exactly one selected Executor owns HOW for each AIOS-node TASK.

The Node project may itself use AIOS-renew as its engineering execution substrate once
interoperability is proven.

Until that point, bootstrap work must preserve the same separation-of-authority principles manually.

## 7. Canonical State

Canonical AIOS-node engineering truth resides in the AIOS-node repository and its exact
TASK/RUN/RESULT/REVIEW lineage once AIOS execution is enabled.

Operational runtime data such as request journals, health status, PID files, service logs,
network observations, and device telemetry are not canonical completion evidence for Node
source changes unless explicitly captured by a Node TASK's deterministic verification contract.

Canonical state of a target repository remains in that target repository, never in
AIOS-node's operational database.

## 8. Request Boundary

Remote requests must be bounded data, not arbitrary shell commands.

Initial production request types should be kept deliberately narrow.

A remote caller may specify an already-authorized operation and its canonical identifiers.
AIOS-node translates that bounded request to an approved AIOS operator surface.

AIOS-node must not accept unrestricted command text as an execution API.

## 9. Retry and Recovery Policy

Transport delivery may be retried.

Canonical execution may not be automatically retried merely because transport, network,
runner, phone, or host state is uncertain.

Duplicate request identity must produce deterministic reuse/no-op behavior.

Unknown execution state requires canonical reconciliation or explicit intervention.

## 10. Git Policy

Do not run generic `git pull`, reset, merge, rebase, stash, checkout recovery, or equivalent
target-repository mutation as prelude to an AIOS operation where AIOS-renew already owns
repository state transition or exact correction lineage.

Initial clone/bootstrap is an operational host concern.

Subsequent engineering repository mutation belongs to canonical AIOS boundaries.

## 11. Verification Policy

Separate Node host qualification from target-project canonical verification.

Node host qualification may test:
- Python availability;
- Git availability;
- shell availability;
- filesystem semantics;
- lock support;
- network access;
- executor binary availability;
- service persistence.

Target-project verification belongs exclusively to AIOS Runtime.

Never duplicate target verification as Node safety ceremony.

## 12. Security Policy

Use least privilege.

Keep control-plane credentials separate from target-repository credentials when practical.

Do not place broad personal credentials on persistent mobile nodes when narrower
repository-scoped authority is sufficient.

Publication credentials should not reside on a Node that does not own publication.

## 13. Task Design Preflight

Before creating every AIOS-node TASK:
1. State the proposed authority.
2. Search AIOS-renew for an existing owner of that authority.
3. Reject the task if it duplicates AIOS-renew.
4. Determine whether the change is Node host lifecycle, transport, security, portability,
   or observability.
5. Define the smallest mutation scope.
6. Define deterministic acceptance criteria.
7. Avoid speculative future multi-node functionality.
8. Preserve one-way dependency on AIOS-renew.

## 14. Roadmap Rule

The initial required sequence is:
1. Governance baseline.
2. Mi 10 Pro host preflight.
3. Pinned AIOS-renew compatibility/bootstrap.
4. Antigravity availability and disposable execution proof.
5. Persistent host service.
6. Bounded dispatch envelope.
7. Private remote wakeup transport.
8. Durable request identity.
9. Crash/reboot reconciliation.
10. Reliability/soak gate.

Codex-on-Android, multi-node routing, automatic recovery, advanced scheduler, and generalized
capability routing remain deferred until measured need exists.

## 15. Completion Criterion

AIOS-node v1 is complete when a Mi 10 Pro can reliably receive an authorized bounded request,
invoke exactly one canonical AIOS execution through the approved operator surface, survive
normal mobile-host lifecycle events without duplicating execution, and expose enough operational
state for deterministic reconciliation—without acquiring any authority already owned by AIOS-renew.
