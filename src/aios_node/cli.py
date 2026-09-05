"""CLI entry point for aios-node."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
from typing import Sequence

from aios_node import __version__
from aios_node.host import Host, HostConfig, OperationalState


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--state-dir",
        default=None,
        help="Directory to store host state snapshot (default: ~/.aios-node/state or $AIOS_NODE_STATE_DIR)",
    )
    parser.add_argument(
        "--aios-bin",
        "--aios-exec",
        dest="aios_bin",
        default=None,
        help="Path or name of configured aios executable",
    )
    parser.add_argument(
        "--antigravity-bin",
        "--agy-bin",
        "--antigravity-exec",
        dest="antigravity_bin",
        default=None,
        help="Path or name of configured antigravity executable",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aios-node",
        description="AIOS-node: Portable operational host for AIOS-renew",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"aios-node {__version__}",
    )

    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # host subcommand
    host_parser = subparsers.add_parser(
        "host",
        help="Run the persistent, non-polling host process",
    )
    _add_common_options(host_parser)
    host_parser.add_argument(
        "--once",
        action="store_true",
        help="Probe readiness, persist state snapshot, and exit without blocking idle",
    )

    # probe subcommand
    probe_parser = subparsers.add_parser(
        "probe",
        help="Probe readiness and print state JSON snapshot to stdout",
    )
    _add_common_options(probe_parser)
    probe_parser.add_argument(
        "--persist",
        action="store_true",
        help="Also atomically persist state snapshot to state file",
    )

    return parser


def _build_config_from_args(args: argparse.Namespace) -> HostConfig:
    state_dir = (
        Path(args.state_dir)
        if args.state_dir
        else (
            Path(os.environ["AIOS_NODE_STATE_DIR"])
            if "AIOS_NODE_STATE_DIR" in os.environ
            else Path.home() / ".aios-node" / "state"
        )
    )

    dependencies: dict[str, str | Path] = {}

    aios_bin = (
        args.aios_bin
        or os.environ.get("AIOS_NODE_AIOS_BIN")
        or os.environ.get("AIOS_BIN")
    )
    if aios_bin:
        dependencies["aios"] = aios_bin

    antigravity_bin = (
        args.antigravity_bin
        or os.environ.get("AIOS_NODE_ANTIGRAVITY_BIN")
        or os.environ.get("ANTIGRAVITY_BIN")
        or os.environ.get("AGY_BIN")
    )
    if antigravity_bin:
        dependencies["antigravity"] = antigravity_bin

    return HostConfig(state_dir=state_dir, dependencies=dependencies)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        parser.print_help()
        return 0

    args = parser.parse_args(argv)
    if not args.subcommand:
        parser.print_help()
        return 0

    config = _build_config_from_args(args)
    host = Host(config=config)

    if args.subcommand == "host":
        state = host.run(once=args.once)
        # Process exits cleanly without launching recovery or child work
        return 0

    elif args.subcommand == "probe":
        state = host.probe()
        if getattr(args, "persist", False):
            try:
                host.persist(state)
            except OSError:
                pass
        sys.stdout.write(state.to_json())
        sys.stdout.flush()
        return 0 if state.operational_state == OperationalState.READY else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
