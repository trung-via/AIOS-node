# N1 — Mi 10 Pro Host Preflight Report

**Status:** PASS  
**Project:** AIOS-node  
**Target host:** Xiaomi Mi 10 Pro / native Termux  
**Purpose:** Establish host capability only. This report does not authorize an AIOS RUN, persistent service, remote wakeup, remediation, repair, publication, or target-repository mutation outside AIOS-renew.

## Result

The Mi 10 Pro host satisfies the N1 minimum mechanics required to proceed to N2 — Pinned AIOS-renew Compatibility.

No proven AIOS-renew kernel defect was established during N1.

One compatibility concern remains intentionally deferred to N2: native Termux resolves `sh` under the Termux prefix rather than `/bin/sh`. N2 must test the pinned AIOS-renew verification path on the real host before deciding whether an upstream portability change is required.

## Observed capability matrix

| Capability | Observed evidence | Result |
| --- | --- | --- |
| CPU architecture | `uname -m` → `aarch64` | PASS |
| Termux private home | `HOME=/data/data/com.termux/files/home` | PASS |
| Termux prefix | `PREFIX=/data/data/com.termux/files/usr` | PASS |
| Login shell | `SHELL=/data/data/com.termux/files/usr/bin/bash` | PASS |
| POSIX `sh` resolution | `command -v sh` → `/data/data/com.termux/files/usr/bin/sh` | PASS / N2 compatibility concern |
| Python | `Python 3.14.6` | PASS |
| Git | `git version 2.55.0` | PASS |
| Filesystem encoding | `utf-8` | PASS |
| Preferred encoding | `utf-8` | PASS |
| stdout encoding | `utf-8` | PASS |
| Python subprocess | `SUBPROCESS_OK` through `sh -c` | PASS |
| POSIX file lock | `fcntl.flock(...LOCK_EX|LOCK_NB)` → `FLOCK_OK` | PASS |
| Private filesystem semantics | create/write/`os.replace`/read/delete → `FILESYSTEM_OK` | PASS |
| DNS | `github.com` resolved successfully | PASS |
| TLS | TLS connection to `github.com:443` → `TLSv1.3` | PASS |
| Storage | ~226 GB total, ~201 GB available at observation time | PASS |
| Memory | ~7.8 GB total RAM; ~2.6 GB available at observation time | PASS |
| Swap | ~6.3 GB total; ~4.0 GB free at observation time | PASS |
| ARM64 LSE atomics | `/proc/cpuinfo` contains `atomics` → `LSE_ATOMICS_OK` | PASS |
| Base Antigravity prerequisites | `curl`, `tar`, `install`, CA bundle, resolver present | PASS |
| Termux glibc repo | `glibc-repo` installed and package index available | PASS |
| Termux glibc loader | `$PREFIX/glibc/lib/ld-linux-aarch64.so.1` executable → `GLIBC_OK` | PASS |
| Antigravity availability before setup | `agy` absent | EXPECTED |
| Antigravity pinned release payload | `v1.1.27` standalone archive | PASS |
| Release payload SHA256 | `304fbb1ff1d7b7fb9848d595ab4d7d4aacc5a9e0bee071d071ad33fec4ab2113` | PASS |
| Archive structure | contains `agy` and `agy.va39` | PASS |
| Antigravity native smoke test | extracted sandbox `agy --version` → `1.1.27` | PASS |
| Android battery policy | Termux set to `No restrictions` | PASS |

## Antigravity provenance boundary

N1 did not install `agy` into the production Termux executable path.

The tested payload was pinned to release `v1.1.27`, and its SHA256 matched the digest published for that GitHub release. The archive was inspected before execution and contained the required twin binaries `agy` and `agy.va39`.

The binary was extracted only into a dedicated smoke-test directory and executed with `--version` to prove native compatibility.

Production installation remains an N2 action because N2 owns the explicit compatibility pin between the host, AIOS-renew, and the executor environment.

## AIOS-renew overlap audit

N1 did **not**:

- author or run a canonical target TASK through AIOS-renew;
- invoke an executor for production engineering work;
- perform target-project canonical verification;
- create EVIDENCE, RESULT, FAILURE, REVIEW, REMEDIATION, or REPAIR artifacts;
- alter AIOS-renew repository semantics;
- add a Node-side mutation lease, dispatcher, reviewer, retry loop, or publisher;
- configure persistent service, boot automation, GitHub Actions, or remote wakeup.

Therefore N1 remains inside the constitutional AIOS-node host/preflight boundary.

## N2 entry conditions

N2 may begin when all of the following remain true:

1. Termux remains in private app storage.
2. Battery policy remains `No restrictions` during compatibility testing.
3. AIOS-renew is selected by an explicit immutable commit SHA or release pin.
4. Antigravity production installation is pinned and provenance-aware.
5. Compatibility testing uses a disposable repository and does not mutate AIOS-renew product state.
6. Any `/bin/sh` incompatibility is reproduced against the pinned AIOS-renew runtime before an upstream fix is proposed.

## N1 verdict

**PASS — proceed to N2: Pinned AIOS-renew Compatibility.**
