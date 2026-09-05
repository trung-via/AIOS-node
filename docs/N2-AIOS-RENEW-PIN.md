# N2 — Pinned AIOS-renew Compatibility Target

**Status:** ACTIVE  
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

N2 compatibility evidence must be attributed to this exact commit. A later AIOS-renew `main` advance does not silently change this compatibility target.

## Declared runtime requirements at the pin

`pyproject.toml` declares:

```text
Python >= 3.11
PyYAML >= 6.0,<7
```

N1 observed Python 3.14.6 on the Mi 10 Pro, satisfying the declared Python version floor. Actual package installation remains an N2 evidence step.

## Known compatibility concern to reproduce

At the pinned commit, `src/aios_renew/verification.py` uses:

```python
return ("/bin/sh", "-c", command)
```

for non-Windows verification execution.

N1 observed native Termux resolving `sh` as:

```text
/data/data/com.termux/files/usr/bin/sh
```

N2 must establish whether `/bin/sh` exists on the real host and, if absent, reproduce the resulting verification-start failure against this exact pinned runtime before proposing any AIOS-renew portability change.

This observation does not authorize AIOS-node to implement a competing verification layer or shell fallback.

## N2 bounded sequence

1. Confirm `/bin/sh` presence/absence on the host.
2. Confirm `pip` availability.
3. Install AIOS-renew from the exact pinned commit into a dedicated Termux virtual environment or otherwise isolated Python environment.
4. Prove the `aios` entry point resolves and reports/help-loads without performing a canonical RUN.
5. Install the already-verified Antigravity v1.1.27 twin binaries into the normal Termux executable path using the pinned payload verified during N1.
6. Prove `agy --version` from the normal PATH.
7. Use a disposable repository to reproduce or clear the pinned verification-shell compatibility concern.
8. Record exact evidence. If a genuine upstream defect is reproduced, stop and open a narrow AIOS-renew portability TASK; do not work around it inside AIOS-node.

## Hard boundaries

N2 must not:

- run a production project TASK;
- add an AIOS-node verification implementation;
- retry or repair canonical AIOS executions;
- modify target repository state outside an explicitly approved disposable compatibility proof;
- install from moving `latest`/`dev` sources when a pinned artifact is available;
- silently move the AIOS-renew pin.

## Gate

N2 passes only when the pinned AIOS-renew operator surface is installable/callable on the Mi 10 Pro and any host incompatibility is deterministically classified without authority overlap.
