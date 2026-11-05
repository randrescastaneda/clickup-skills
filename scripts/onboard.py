"""Finish guided onboarding: hosted OAuth in the agent OR local token-based CLI.

This module does not access the hosted OAuth session or read/log ClickUp tokens.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys

CLICKUP_SETTINGS_URL = "https://app.clickup.com/settings/apps"
CLIENT_CHOICES = (
    ("1", "kilo", "Kilo Code"),
    ("2", "codex", "Codex"),
    ("3", "claude", "Claude Code"),
    ("4", "copilot", "GitHub Copilot"),
)


def choose_client(interactive: bool | None = None, prompt=input) -> str:
    """Choose a supported agent; Enter selects Kilo. --client bypasses this."""
    if interactive is None:
        interactive = sys.stdin.isatty()
    if not interactive:
        print("No interactive terminal detected; using Kilo Code. Pass --client to choose another agent.")
        return "kilo"
    print("\nWhich coding agent are you installing for?")
    for number, _, label in CLIENT_CHOICES:
        print(f"  {number}. {label}{' (default)' if number == '1' else ''}")
    options = {number: client for number, client, _ in CLIENT_CHOICES}
    options.update({client: client for _, client, _ in CLIENT_CHOICES})
    while True:
        answer = prompt("Choose agent [1]: ").strip().lower()
        if not answer:
            return "kilo"
        if answer in options:
            return options[answer]
        print("Choose 1-4, or enter kilo, codex, claude, or copilot.")


def authenticate_clickup(cup_command: list[str], interactive: bool | None = None) -> None:
    """Reuse valid credentials; otherwise delegate the token prompt to cup."""
    if subprocess.run(cup_command + ["auth"], check=False).returncode == 0:
        print("\nClickUp: existing authentication verified.")
        return
    if interactive is None:
        interactive = sys.stdin.isatty()
    if not interactive:
        raise ValueError(
            "ClickUp needs an interactive sign-in. Rerun onboard in a terminal, "
            "or configure your existing ClickUp CLI credentials first."
        )
    print("\nClickUp: sign in to your account in a browser.")
    print("1. Open " + CLICKUP_SETTINGS_URL)
    print("2. Under API Token, generate or copy your personal token (starts with pk_).")
    print("3. Return here; cup will ask for your token and Workspace ID.")
    print("   The Workspace ID is the number in your ClickUp app URL.")
    print("   Never paste the token into an agent chat, repository, or command line.")
    input("Press Enter when ready to configure ClickUp...")
    subprocess.run(cup_command + ["init"], check=True)
    subprocess.run(cup_command + ["auth"], check=True)
    print("ClickUp: authentication verified.")


def authenticate_github(gh_path: str | None = None, interactive: bool | None = None) -> None:
    """Use gh's browser login only when no valid active GitHub account exists."""
    gh = gh_path or shutil.which("gh")
    if not gh:
        raise ValueError(
            "GitHub CLI (gh) is required for local GitHub workflows. "
            "Install it from https://cli.github.com/ and rerun the SAME onboard command. "
            "Your ClickUp setup is preserved."
        )
    status = [gh, "auth", "status", "--hostname", "github.com"]
    if subprocess.run(status, check=False, stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL).returncode == 0:
        print("\nGitHub: existing authentication verified.")
        return
    if interactive is None:
        interactive = sys.stdin.isatty()
    if not interactive:
        raise ValueError("GitHub sign-in requires an interactive terminal. Rerun onboard locally.")
    print("\nGitHub: a browser authorization is needed. Follow GitHub CLI's prompts.")
    subprocess.run([gh, "auth", "login", "--hostname", "github.com", "--web"], check=True)
    subprocess.run(status, check=True)
    print("GitHub: authentication verified.")


def resolve_backends(mode: str | None = None, github: str | None = None) -> tuple[str, str]:
    """Choose both services before any settings, runtime or authentication writes."""
    mode = {"oauth": "remote-only", "cli": "local-helper"}.get(mode, mode or "hosted")
    if mode not in ("hosted", "remote-only", "local-helper"):
        raise ValueError("Unknown onboarding mode.")
    github = github or ("hosted" if mode == "remote-only" else "cli")
    if github not in ("cli", "hosted"):
        raise ValueError("Unknown GitHub backend.")
    if mode == "remote-only" and github != "hosted":
        raise ValueError("remote-only requires --github hosted; gh is not permitted in that mode.")
    if mode == "local-helper" and github != "cli":
        raise ValueError("The local helper requires --github cli; use --mode hosted for hosted GitHub.")
    return mode, github


def run_onboarding(runtime: Path | None, *, mode: str = "hosted", github: str | None = None) -> None:
    """Finish CLI or hosted-MCP setup without exchanging credentials between them."""
    mode, github = resolve_backends(mode, github)
    if mode == "local-helper":
        if runtime is None:
            raise ValueError("The full helper requires an installed runtime.")
        metadata_path = runtime / "runtime.json"
        if not metadata_path.is_file():
            raise ValueError("The installed runtime is missing. Rerun onboard --mode cli.")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        cup_command = metadata.get("cup_command")
        if not isinstance(cup_command, list) or not cup_command or not all(
            isinstance(item, str) and item for item in cup_command
        ):
            raise ValueError("The installed ClickUp CLI command is missing or invalid.")
        authenticate_clickup(cup_command)
        authenticate_github()
    if mode in ("hosted", "remote-only"):
        if github == "cli":
            authenticate_github()
        print("\nTerminal setup complete: official ClickUp MCP configured; ClickUp OAuth still needs verification.")
        print("ClickUp OAuth is NOT authenticated or verified by this terminal command.")
        print("Restart/reload the agent, authorize clickup_official using its browser OAuth prompt,")
        print("and verify read-only Workspace/task access and discovered schemas.")
        print("This mode uses agent-directed host tools, NOT the helper's durable journal or scope enforcement.")
        if github == "cli":
            print("GitHub: reuse the verified gh sign-in across authorized repositories; verify each target repository in the agent.")
            print("No GitHub MCP or manually created repository-specific token is required for this selected backend.")
        else:
            print("GitHub: verify an approved hosted GitHub connection in the agent; STOP if unavailable.")
            print("Do not install or use gh as fallback for the selected hosted GitHub backend.")
        print("Missing or banned ClickUp MCP: STOP. Do not install cup, cu-work, a local helper, or mcp-remote as fallback.")
        print("Never route a failed or uncertain host write through the unauthenticated local helper.")
    else:
        print("\nTerminal setup complete: full local helper, skills, MCP configuration, and CLI sign-ins verified.")
        print("Restart/reload your coding agent to verify actual MCP and skill discovery.")
        print("The hosted GitHub MCP may request separate OAuth authorization.")
        print("Local helper safeguards depend on a verified project binding.")
    print("ClickUp's native GitHub integration handles configured links/activity; agent GitHub access is separate.")
    print("No native connection, automation, repository permission or Workspace access is enabled here.")
