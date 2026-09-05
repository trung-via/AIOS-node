# AIOS-node Constitution

**Status:** Constitutional Baseline v1.0  
**Scope:** AIOS-node authority, boundaries, portability, lifecycle, and interaction with AIOS-renew

## 1. Constitutional Inheritance

AIOS-node is a subordinate operational component of the wider AIOS architecture.

AIOS-node inherits the purpose and constitutional principles of the canonical AIOS
Manifesto and AIOS Constitution. This Constitution may narrow AIOS-node authority but
may never broaden, override, reinterpret, or replace AIOS constitutional authority.

When AIOS-node integrates with AIOS-renew, canonical AIOS engineering contracts and
exact repository state remain authoritative over Node operational state.

## 2. Host, Not Orchestrator

AIOS-node exists to host, wake, supervise, observe, and reliably deliver already-authorized
AIOS execution.

AIOS-node is not a Brain, Planner, Dispatcher, Executor, Runtime, Reviewer, Repair authority,
Remediation authority, or Publisher.

It must never acquire those roles implicitly because it happens to run on the machine that
hosts them.

## 3. Canonical Truth Remains Outside the Node

AIOS-node operational state is never canonical engineering truth.

TASK, RUN, RESULT, FAILURE, EVIDENCE, REVIEW, REMEDIATION, REPAIR, source SHA,
verification status, and publication status remain governed by their canonical AIOS
contracts and repositories.

Node records may describe delivery and host observations only.

## 4. One-way Dependency

AIOS-node may depend on a pinned and explicitly compatible AIOS-renew interface.

AIOS-renew must not depend on AIOS-node for its canonical execution, verification,
review, or evidence semantics.

Failure or absence of AIOS-node must not change the meaning of canonical AIOS artifacts.

## 5. No Duplicate Execution Authority

AIOS-node must invoke canonical AIOS operator surfaces rather than directly invoking
native coding Executors for production work.

Executor selection must already be authorized by Human/Brain contract or canonical request input.

AIOS-node must not infer, substitute, reroute, retry, downgrade, upgrade, or otherwise choose
another Executor or model.

## 6. No Duplicate Repository Authority

AIOS-node must not reproduce AIOS repository admission, synchronization, mutation locking,
SHA binding, scope enforcement, completion gates, or correction-lineage logic.

Node workspace management may establish that a repository exists and is accessible, but
canonical repository transitions belong to AIOS-renew or another explicitly authorized
repository authority.

## 7. No Duplicate Verification or Semantic Judgment

AIOS-node must not execute project canonical verification on behalf of Runtime, construct
canonical EVIDENCE, judge semantic completion, review implementation quality, or turn
operational logs into engineering claims.

Node may perform device and host preflight checks solely to establish whether the host can
safely attempt delivery.

## 8. Delivery Idempotency Is Not Execution Retry

AIOS-node may deduplicate transport requests and make duplicate delivery events deterministic no-ops.

It must not interpret delivery idempotency as authority to retry an admitted AIOS execution.

When prior execution state is uncertain, Node must reconcile canonical state or fail closed
rather than start another execution.

## 9. Reconciliation Is Observation, Not Recovery Authority

After crash, reboot, disconnect, or process loss, AIOS-node may inspect canonical state to
determine whether the associated request has a known terminal state.

It must not autonomously invoke REMEDIATION, REPAIR, replacement PRIMARY execution,
publication, fallback, or other corrective engineering action unless a future explicit
canonical contract separately authorizes that exact action.

## 10. Host State and Engineering State Are Separate

Node lifecycle states describe the host only.

Examples:
- READY
- BUSY
- DEGRADED
- OFFLINE

They must never replace or masquerade as canonical AIOS verdicts or execution states.

## 11. Bounded and Minimum-Privilege Operation

AIOS-node must use the minimum credentials, filesystem authority, network authority,
runtime permissions, concurrency, storage, background activity, and power consumption
necessary for its current role.

Credentials for wakeup, source access, execution, review, and publication must not be
unnecessarily combined.

## 12. Observable and Attributable Automation

Every accepted remote request must have stable identity.

Every Node action that can start an AIOS invocation must be attributable to that request.

Crash, restart, duplicate delivery, process exit, and reconciliation outcomes must remain
explainable without inventing canonical engineering truth.

## 13. Portability Before Device Specialization

AIOS-node is a portable execution-host framework.

Android/Termux, Windows, Linux, ARM64, laptop, phone, mini-PC, or server support should be
expressed as thin host adapters or capability probes.

Device-specific behavior must not leak into canonical AIOS execution semantics.

Mi 10 Pro is the first target node, not the architectural definition of AIOS-node.

## 14. Evidence Before Expansion

New Node capabilities, retries, schedulers, routing, multi-node coordination, background
services, or autonomous actions require evidence of a real operational need.

Do not build anticipated orchestration merely because it may become useful later.

## 15. North Star

AIOS-node exists to increase:

**Verified Useful Work / (Time + Tokens + Human Effort)**

Additional daemons, services, retries, queues, agents, models, abstractions, telemetry,
or automation are justified only when they measurably improve useful work enough to
justify their complexity, resource use, failure modes, and authority risk.

## 16. Constitutional Change

Only explicit Human authority may change this Constitution.

Implementation convenience, device limitations, executor behavior, transport failures,
or model suggestions cannot silently expand AIOS-node authority.
