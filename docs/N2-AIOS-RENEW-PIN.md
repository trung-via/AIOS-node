# N2 — Pinned AIOS-renew Compatibility Target

**Status:** PASS / COMPLETE  
**AIOS-node phase:** N2  
**Target host:** Xiaomi Mi 10 Pro / native Termux

## Canonical upstream pin

Repository: `trung-via/AIOS-renew`

Pinned commit:

```text
5bdaa603924ac6104ed28413ad91a4cc1b7f6d0b
```

Observed canonical branch at pin selection time:

```text
main -> 5bdaa603924ac6104ed28413ad91a4cc1b7f6d0b
```

Commit message:

```text
task: rebase TASK-058 historical recovery on current canonical state
```

N2 compatibility evidence is attributed to this exact commit. A later AIOS-renew `main` advance does not silently change this compatibility target.

## Declared runtime requirements at the pin

`pyproject.toml` declares:

```text
Python >= 3.11
PyYAML >= 6.0,<7
```

N2 installed the exact pin successfully inside a dedicated Termux virtual environment using Python 3.14.6 and PyYAML 6.0.3.

## Verification-shell concern — cleared on this host

At the pinned commit, `src/aios_renew/verification.py` uses:

```python
return ("/bin/sh", "-c", command)
```

for non-Windows verification execution.

N1 observed native Termux resolving ordinary `sh` as:

```text
/data/data/com.termux/files/usr/bin/sh
```

N2 then proved on the real Mi 10 Pro host that:

```text
/bin/sh exists and is executable
Python subprocess(['/bin/sh','-c','printf BIN_SH_EXEC_OK']) -> RC=0
stdout -> b'BIN_SH_EXEC_OK'
stderr -> b''
```

Therefore the concern is **cleared for this specific host/runtime combination** and no upstream AIOS-renew portability change is authorized by current evidence.

This does not claim universal Android/Termux portability across other hosts.

## Completed N2 sequence

1. `/bin/sh` presence and execution verified.
2. `pip` availability verified.
3. AIOS-renew installed from the exact pinned commit into `$HOME/.venvs/aios-renew-5bdaa603`.
4. `aios --help` loaded successfully without a canonical RUN.
5. Antigravity v1.1.27 twin binaries installed from the N1 hash-verified pinned payload.
6. `agy --version` resolved from normal Termux PATH and reported `1.1.27`.
7. Google OAuth authentication completed and cached.
8. Headless Antigravity invocation succeeded with Gemini 3.8 Flash / high.
9. A disposable Git repository was created at `$HOME/aios-node-smoke`.
10. The pinned AIOS operator loaded and rendered `TASK-N2-SMOKE` via `aios task` without entering execution.
11. Exact installed AIOS provenance was verified through Python distribution metadata: both `commit_id` and `requested_revision` equal the pinned commit.

Canonical evidence report: [`N2-MI10-COMPATIBILITY-REPORT.md`](N2-MI10-COMPATIBILITY-REPORT.md).

## Hard boundaries preserved

N2 did not:

- run a production project TASK;
- admit an AIOS RUN;
- add an AIOS-node verification implementation;
- retry or repair canonical AIOS executions;
- modify target repository state outside the approved disposable compatibility proof;
- install Antigravity from moving `latest`/`dev` sources;
- silently move the AIOS-renew pin;
- trust the entire Termux `$HOME` to the executor.

## Gate

N2 gate:

> The pinned AIOS-renew operator surface is installable/callable on the Mi 10 Pro and any host incompatibility is deterministically classified without authority overlap.

Result: **PASS**.

Next phase: **N3 — Disposable End-to-End Execution Proof**.
