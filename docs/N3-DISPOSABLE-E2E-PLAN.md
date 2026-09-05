# N3 — Disposable End-to-End Execution Plan

**Status:** PASS  
**Project:** AIOS-node  
**Target host:** Xiaomi Mi 10 Pro / native Termux  
**Pinned AIOS-renew:** `5bdaa603924ac6104ed28413ad91a4cc1b7f6d0b`

## Goal

Prove exactly one disposable canonical PRIMARY execution on the Mi 10 Pro through the pinned AIOS-renew Runtime and exactly one Antigravity executor.

N3 is an integration proof, not an AIOS-node orchestration implementation phase.

## Constitutional decision

N3 will **not** add a second dispatcher, verifier, task parser, executor launcher, retry loop, or publication layer to AIOS-node.

For this phase only, the Human issues one bounded local `aios run ... --executor antigravity` command. That command is the temporary bootstrap surface used to prove the substrate before AIOS-node host/request code exists.

AIOS-renew remains sole owner of:
- PRIMARY synchronization/admission;
- repository mutation authority;
- Antigravity invocation;
- model/effort selection;
- Runtime verification;
- RUN / RESULT / FAILURE state;
- terminal transport.

## Disposable repository topology

Use the existing Termux disposable worktree:

```text
$HOME/aios-node-smoke
```

Before the first N3 RUN it must be converted into a valid PRIMARY target:

```text
clean attached branch: main
configured upstream: origin/main
remote: disposable local bare Git repository
```

Recommended disposable remote:

```text
$HOME/aios-node-smoke-remote.git
```

The local bare remote is intentional for N3. It satisfies AIOS-renew's upstream synchronization and Git-ref transport mechanics without mutating `AIOS-node`, `AIOS-renew`, Python Agent, or any production GitHub repository. Remote Internet wakeup is deferred to N6.

## Baseline preparation gate

Before `aios run`:
- repository-local Git author identity exists;
- branch is `main`;
- baseline files and TASK are committed;
- `origin/main` exists and tracks the exact baseline commit;
- `git status --porcelain` is empty;
- `git rev-parse HEAD` equals `git rev-parse origin/main`;
- pinned `aios` executable and production `agy` remain callable.

Do not bypass AIOS PRIMARY synchronization. N3 must satisfy its contract.

## N3 smoke TASK

The canonical disposable TASK may modify exactly one file:

```text
SMOKE.txt
```

Required content:

```text
AIOS_NODE_N3_OK\n
```

The executor must commit the implementation and must not push. Runtime owns verification and transport.

Recommended canonical verification:

```text
python -c "from pathlib import Path; assert Path('SMOKE.txt').read_bytes() == b'AIOS_NODE_N3_OK\\n'"
```

## Execution

Exactly one command is authorized after baseline preparation:

```text
aios run TASK-N3-SMOKE --executor antigravity --repo <disposable-worktree>
```

No direct production `agy` invocation is allowed for the TASK.

## PASS evidence

N3 passes only if all of the following are observed:
- one canonical RUN identity is admitted;
- exactly one Antigravity native invocation occurs;
- final Git HEAD advances by the authorized committed delta only;
- `SMOKE.txt` has exact required bytes;
- Runtime executes canonical verification;
- canonical RESULT exists and binds the final HEAD;
- terminal transport produces the expected immutable AIOS refs/artifacts on the disposable remote;
- worktree is clean after completion;
- no retry, fallback, remediation, repair, second verifier, or manual executor intervention occurs.

## Failure rule

If the N3 RUN fails, stop and inspect the canonical FAILURE / observation / transport state. Do not rerun PRIMARY automatically and do not manually patch around AIOS-renew.

A reproduced host/runtime defect is classified first; only then may a narrow upstream fix be proposed.

## Non-goals

- no GitHub Actions runner;
- no persistent service;
- no bounded remote request schema yet;
- no delivery dedupe;
- no crash reconciliation;
- no Codex Android parity;
- no AIOS-node production executor wrapper.

## Result

PASS. Canonical execution:

```text
RUN-N3-SMOKE-001
base_sha: b27c7aeb4f1ca8c3b222400adb17df435d32da40
head_sha: 570da336cb2959e98f162753f116c2c61f160677
executor: antigravity
```

See [`N3-MI10-E2E-REPORT.md`](N3-MI10-E2E-REPORT.md) for the attributable evidence and authority audit.
