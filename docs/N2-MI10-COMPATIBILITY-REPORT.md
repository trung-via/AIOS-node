# N2 — Mi 10 Pro Pinned AIOS-renew Compatibility Report

**Status:** PASS  
**Project:** AIOS-node  
**Target host:** Xiaomi Mi 10 Pro / native Termux  
**Pinned AIOS-renew commit:** `5bdaa603924ac6104ed28413ad91a4cc1b7f6d0b`

## Result

The Mi 10 Pro host satisfies the N2 gate for pinned AIOS-renew compatibility.

The exact pinned AIOS-renew runtime is installable and callable in an isolated Termux Python environment. Antigravity CLI 1.1.27 is installed from the previously hash-verified pinned payload, Google OAuth is established, headless model invocation succeeds with `gemini-3.8-flash` / `high`, and the pinned AIOS operator successfully loads and validates a canonical TASK in a disposable Git repository without entering a RUN.

No AIOS-renew portability defect was reproduced during N2. The N1 `/bin/sh` concern is cleared for this specific host/runtime combination.

## Compatibility evidence

| Capability | Observed evidence | Result |
| --- | --- | --- |
| Pinned AIOS-renew identity | `commit_id` and `requested_revision` both equal `5bdaa603924ac6104ed28413ad91a4cc1b7f6d0b` in installed distribution metadata | PASS |
| Isolated Python environment | dedicated venv `$HOME/.venvs/aios-renew-5bdaa603`, Python 3.14.6 | PASS |
| pip availability | pip 26.2.1 available in native Termux Python | PASS |
| AIOS package install | `aios-renew-0.1.3` and `PyYAML-6.0.3` installed successfully from exact Git commit | PASS |
| AIOS entry point | pinned `aios --help` loads without traceback | PASS |
| `/bin/sh` presence | executable `/bin/sh` exists on host | PASS |
| `/bin/sh` subprocess execution | Python subprocess `['/bin/sh','-c','printf BIN_SH_EXEC_OK']` returned `RC=0`, expected stdout, empty stderr | PASS |
| Antigravity pinned binary | `$PREFIX/bin/agy` resolves and reports `1.1.27` | PASS |
| Antigravity twin payload | `agy` and `agy.va39` installed from the N1 hash-verified v1.1.27 archive | PASS |
| Google OAuth | interactive authentication completed successfully | PASS |
| Workspace authority | full Termux `$HOME` was not trusted; isolated `$HOME/aios-node-smoke` workspace used instead | PASS |
| Model profile | Antigravity reports Gemini 3.8 Flash / High | PASS |
| Headless authentication | non-interactive print invocation returned exactly `HEADLESS_AUTH_OK` | PASS |
| Disposable Git repository | `$HOME/aios-node-smoke` initialized as an isolated Git repository | PASS |
| Canonical TASK parser/operator | pinned `aios task TASK-N2-SMOKE --repo "$HOME/aios-node-smoke"` rendered TASK id, revision, goal, acceptance and verification without execution | PASS |

## Cleared compatibility concern

At the pinned AIOS-renew commit, non-Windows Runtime verification constructs:

```python
("/bin/sh", "-c", command)
```

N1 had observed that ordinary Termux shell resolution points under the Termux prefix, creating a portability concern. N2 proved on the actual Mi 10 Pro host that `/bin/sh` exists, is executable, and works through the same Python subprocess shape relevant to AIOS verification startup.

Therefore this concern is classified **CLEARED ON THIS HOST**. No upstream AIOS-renew shell portability TASK is justified by current evidence.

This does not claim universal Android/Termux portability across other devices or Termux builds.

## Authority and boundary audit

N2 preserved the AIOS-node constitutional boundary:

- no production TASK was executed;
- no AIOS RUN was admitted;
- AIOS-node did not implement its own verification layer;
- AIOS-node did not invoke an executor on behalf of a canonical RUN;
- no remediation, repair, retry, publication or transport authority was duplicated;
- no AIOS-renew source was modified;
- the AIOS-renew compatibility target remained pinned to one immutable commit;
- executor trust was bounded to a disposable workspace instead of the Termux home directory.

## N2 gate

Gate requirement:

> `aios` is callable on the Mi 10 Pro against a disposable repository without architecture drift.

Observed result: **PASS**.

## Next phase

Proceed to **N3 — Disposable End-to-End Execution Proof**.

N3 is the first phase allowed to admit one disposable canonical AIOS PRIMARY execution through:

```text
AIOS operator
  -> AIOS-renew Dispatcher/Runtime
  -> exactly one Antigravity executor
  -> Runtime-owned verification
  -> canonical RESULT or FAILURE
```

N3 must not bypass AIOS by invoking `agy` directly for the execution proof.
