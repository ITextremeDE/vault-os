"""Command-line interface for Vault-OS lifecycle operations."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .agents import doctor_agents, initialize_agents
from .bootstrap import BootstrapPlan, bootstrap_vault
from .operations import (
    Plan,
    diff_installation,
    doctor,
    execute_device_sync,
    execute_install,
    execute_update,
    prepare_install_config,
    vault_root,
)
from .package import ConflictError, Package, VaultOSError
from .providers import provider_ids


DEFAULT_PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        prog="vault-os",
        description="Install, synchronize, and safely update Vault-OS in an Obsidian vault.",
    )
    value.add_argument(
        "--package-root",
        type=Path,
        default=DEFAULT_PACKAGE_ROOT,
        help=argparse.SUPPRESS,
    )
    commands = value.add_subparsers(dest="command", required=True)

    install = commands.add_parser("install", help="Install into a new or existing vault directory.")
    install.add_argument("vault", type=Path)
    install.add_argument("--config", type=Path, help="Use an instance configuration instead of the neutral seed.")
    install.add_argument("--name", help="Set the vault name; defaults to the target directory name.")
    install.add_argument("--system-root", help="Override paths.system in the installed configuration.")
    selection = install.add_mutually_exclusive_group()
    selection.add_argument(
        "--module",
        action="append",
        dest="modules",
        help="Select an optional module; repeat for multiple modules.",
    )
    selection.add_argument(
        "--all-modules",
        action="store_true",
        help="Select every module in the package catalog.",
    )
    install.add_argument("--json", action="store_true", help="Emit machine-readable output.")

    update = commands.add_parser("update", help="Apply the current package without overwriting local changes.")
    update.add_argument("vault", type=Path)
    update.add_argument("--json", action="store_true", help="Emit machine-readable output.")

    difference = commands.add_parser("diff", help="Show the update plan without changing the vault.")
    difference.add_argument("vault", type=Path)
    difference.add_argument("--json", action="store_true", help="Emit machine-readable output.")

    health = commands.add_parser("doctor", help="Check package and installation integrity without changing files.")
    health.add_argument("vault", type=Path)
    health.add_argument(
        "--ai",
        action="store_true",
        help="Also validate initialized agent providers, skills, and optional QMD integration.",
    )
    health.add_argument("--json", action="store_true", help="Emit machine-readable output.")

    bootstrap = commands.add_parser(
        "bootstrap",
        help="Create missing user-owned start files without overwriting existing content.",
    )
    bootstrap.add_argument("vault", type=Path)
    bootstrap.add_argument(
        "--json", action="store_true", help="Emit machine-readable output."
    )

    device_sync = commands.add_parser(
        "device-sync",
        help="Verify files delivered by vault sync and rebuild device-local release state.",
    )
    device_sync.add_argument("vault", type=Path)
    device_sync.add_argument(
        "--json", action="store_true", help="Emit machine-readable output."
    )

    agents = commands.add_parser(
        "agent-init",
        help="Initialize provider-native agent instructions, skills, and optional QMD integration.",
    )
    agents.add_argument("vault", type=Path)
    agents.add_argument(
        "--provider",
        choices=(*provider_ids(), "all"),
        default="all",
        help="Provider adapter to initialize; defaults to every registered adapter.",
    )
    agents.add_argument(
        "--qmd",
        action="store_true",
        help="Enable a project-local QMD index and MCP configuration.",
    )
    agents.add_argument(
        "--qmd-command",
        default="qmd",
        help="QMD executable name or path; used only when --qmd is supplied.",
    )
    agents.add_argument("--json", action="store_true", help="Emit machine-readable output.")
    return value


def print_plan(plan: Plan, *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(plan.as_dict(), ensure_ascii=False, indent=2))
        return
    title = "Vault-OS " + plan.operation
    print(title)
    if plan.release_from is None:
        print(f"Release: {plan.release_to}")
    else:
        print(f"Release: {plan.release_from} -> {plan.release_to}")
    modules = ", ".join(plan.modules_to) if plan.modules_to else "none"
    print(f"Modules: {modules}")
    counts = plan.counts()
    print(
        "Changes: "
        f"add={counts['add']}, update={counts['update']}, "
        f"remove={counts['remove']}, seed={counts['seed']}, "
        f"unchanged={counts['unchanged']}"
    )
    if counts["instancePreserved"]:
        print(f"Instance files preserved: {counts['instancePreserved']}")
    visible = [change for change in plan.changes if change.category != "lock"]
    for change in visible:
        print(f"- {change.category}: {change.target}")
    if plan.conflicts:
        print("Conflicts:")
        for conflict in plan.conflicts:
            print(f"- {conflict}")
    elif not visible:
        if counts["lock"]:
            print("Device-local release metadata updated.")
        else:
            print("Installation is up to date.")


def print_doctor(result: dict[str, object], *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print("Vault-OS doctor")
    print("Status: healthy" if result["healthy"] else "Status: unhealthy")
    details = result.get("details", {})
    if isinstance(details, dict):
        if details.get("installedVersion"):
            print(f"Installed release: {details['installedVersion']}")
        if details.get("packageVersion"):
            print(f"Package release: {details['packageVersion']}")
    warnings = result.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    errors = result.get("errors", [])
    if isinstance(errors, list) and errors:
        print("Errors:")
        for error in errors:
            print(f"- {error}")


def print_agent_init(result: dict[str, object], *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    providers = ", ".join(result["providers"])  # type: ignore[arg-type]
    print("Vault-OS agent initialization")
    print(f"Providers: {providers}")
    print(f"Registered skills: {result['skills']}")
    qmd = result["qmd"]
    if isinstance(qmd, dict):
        state = "enabled" if qmd["enabled"] else "disabled"
        availability = "available" if qmd["available"] else "not available"
        print(f"QMD: {state}; command {qmd['command']!r} is {availability}")
    counts = result["counts"]
    if isinstance(counts, dict):
        print(
            "Changes: "
            f"created={counts['created']}, updated={counts['updated']}, "
            f"removed={counts['removed']}, unchanged={counts['unchanged']}"
        )
    warnings = result.get("warnings", [])
    if isinstance(warnings, list) and warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")


def print_bootstrap(plan: BootstrapPlan, *, json_output: bool) -> None:
    report = plan.as_dict()
    if json_output:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return
    print("Vault-OS bootstrap")
    counts = report["counts"]
    print(
        "Files: "
        f"created={counts['created']}, preserved={counts['preserved']}, "
        f"skipped={counts['skipped']}"
    )
    for target in report["created"]:
        print(f"- created: {target}")
    for target in report["preserved"]:
        print(f"- preserved: {target}")
    for reason in report["skipped"]:
        print(f"- skipped: {reason}")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        package = Package.load(args.package_root)
        if args.command == "install":
            vault = vault_root(args.vault, create=True)
            config = prepare_install_config(
                package,
                vault,
                args.config,
                args.name,
                args.system_root,
                args.modules,
                args.all_modules,
            )
            plan = execute_install(package, vault, config)
            print_plan(plan, json_output=args.json)
            return 0
        vault = vault_root(args.vault)
        if args.command == "bootstrap":
            plan = bootstrap_vault(package, vault)
            print_bootstrap(plan, json_output=args.json)
            return 0
        if args.command == "agent-init":
            result = initialize_agents(
                package,
                vault,
                args.provider,
                args.qmd,
                args.qmd_command,
            )
            print_agent_init(result, json_output=args.json)
            return 0
        if args.command == "update":
            plan = execute_update(package, vault)
            print_plan(plan, json_output=args.json)
            return 0
        if args.command == "device-sync":
            plan = execute_device_sync(package, vault)
            print_plan(plan, json_output=args.json)
            return 0
        if args.command == "diff":
            plan = diff_installation(package, vault)
            print_plan(plan, json_output=args.json)
            return ConflictError.exit_code if plan.conflicts else 0
        if args.command == "doctor":
            result = doctor(package, vault)
            if args.ai and result["healthy"]:
                agent_result = doctor_agents(package, vault)
                result["details"]["agents"] = agent_result["details"]
                result["warnings"].extend(
                    f"agent: {warning}" for warning in agent_result["warnings"]
                )
                result["errors"].extend(
                    f"agent: {error}" for error in agent_result["errors"]
                )
                result["healthy"] = not result["errors"]
            print_doctor(result, json_output=args.json)
            return 0 if result["healthy"] else 1
        raise VaultOSError(f"unsupported command: {args.command}")
    except VaultOSError as error:
        print(f"vault-os: {error}", file=sys.stderr)
        return error.exit_code
    except OSError as error:
        print(f"vault-os: filesystem error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
