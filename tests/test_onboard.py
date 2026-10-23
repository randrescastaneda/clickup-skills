"""Offline tests for the interactive one-command onboarding flow."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("onboard", ROOT / "scripts/onboard.py")
onboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(onboard)


def completed(exit_code: int) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess([], exit_code)


class ChooseClientTests(unittest.TestCase):
    def test_kilo_is_default(self):
        self.assertEqual(onboard.choose_client(interactive=True, prompt=lambda _: ""), "kilo")
        self.assertEqual(onboard.choose_client(interactive=False), "kilo")

    def test_all_supported_choices(self):
        for selected, expected in (("1", "kilo"), ("2", "codex"), ("3", "claude"),
                                   ("4", "copilot"), ("CoDeX", "codex")):
            self.assertEqual(onboard.choose_client(interactive=True,
                                                   prompt=lambda _, v=selected: v), expected)

    def test_invalid_choice_is_reprompted(self):
        answers = iter(("something else", "3"))
        self.assertEqual(onboard.choose_client(interactive=True, prompt=lambda _: next(answers)), "claude")


class ClickUpAuthTests(unittest.TestCase):
    def test_valid_credentials_are_reused_without_init(self):
        cup = ["node", "/private tools/cup.js"]
        with patch.object(onboard.subprocess, "run", return_value=completed(0)) as run:
            onboard.authenticate_clickup(cup, interactive=False)
        run.assert_called_once_with(cup + ["auth"], check=False)

    def test_missing_credentials_trigger_interactive_init_and_verification(self):
        cup = ["node", "/private tools/cup.js"]
        with patch.object(onboard.subprocess, "run",
                          side_effect=[completed(1), completed(0), completed(0)]) as run, \
             patch("builtins.input", return_value=""):
            onboard.authenticate_clickup(cup, interactive=True)
        self.assertEqual(run.call_count, 3)
        self.assertEqual(run.call_args_list[1].args[0], cup + ["init"])
        self.assertEqual(run.call_args_list[2].args[0], cup + ["auth"])

    def test_missing_credentials_without_tty_fails_before_init(self):
        with patch.object(onboard.subprocess, "run", return_value=completed(1)) as run:
            with self.assertRaisesRegex(ValueError, "interactive"):
                onboard.authenticate_clickup(["node", "cup.js"], interactive=False)
        self.assertEqual(run.call_count, 1)


class GitHubAuthTests(unittest.TestCase):
    def test_reuse_valid_github_signin(self):
        with patch.object(onboard.subprocess, "run", return_value=completed(0)) as run:
            onboard.authenticate_github("/opt/bin/gh")
        self.assertEqual(run.call_count, 1)
        self.assertEqual(run.call_args.args[0],
                         ["/opt/bin/gh", "auth", "status", "--hostname", "github.com"])

    def test_browser_login_only_when_missing(self):
        with patch.object(onboard.subprocess, "run",
                          side_effect=[completed(1), completed(0), completed(0)]) as run:
            onboard.authenticate_github("/opt/bin/gh", interactive=True)
        self.assertEqual(run.call_count, 3)
        self.assertEqual(run.call_args_list[1].args[0],
                         ["/opt/bin/gh", "auth", "login", "--hostname", "github.com", "--web"])
        self.assertEqual(run.call_args_list[2].args[0],
                         ["/opt/bin/gh", "auth", "status", "--hostname", "github.com"])

    def test_missing_gh_reports_single_command_retry(self):
        with patch.object(onboard.shutil, "which", return_value=None):
            with self.assertRaisesRegex(ValueError, "SAME onboard command"):
                onboard.authenticate_github()

    def test_no_browser_login_without_tty(self):
        with patch.object(onboard.subprocess, "run", return_value=completed(1)) as run:
            with self.assertRaisesRegex(ValueError, "interactive"):
                onboard.authenticate_github("/opt/bin/gh", interactive=False)
        self.assertEqual(run.call_count, 1)


class OrchestrationTests(unittest.TestCase):
    def test_runtime_command_is_reused_without_exposing_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "runtime.json").write_text(json.dumps({
                "cup_command": ["node", "/runtime/tools/cup.js"]
            }), encoding="utf-8")
            with patch.object(onboard, "authenticate_clickup") as cup, \
                 patch.object(onboard, "authenticate_github") as gh:
                onboard.run_onboarding(folder, mode="cli")
            cup.assert_called_once_with(["node", "/runtime/tools/cup.js"])
            gh.assert_called_once_with()

    def test_corrupt_runtime_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "runtime.json").write_text('{"cup_command":"not an argv list"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing or invalid"):
                onboard.run_onboarding(folder, mode="cli")

    def test_oauth_mode_uses_github_only_no_runtime_or_clickup_token(self):
        with patch.object(onboard, "authenticate_clickup") as cup, \
             patch.object(onboard, "authenticate_github") as gh:
            onboard.run_onboarding(None, mode="oauth")
        cup.assert_not_called()
        gh.assert_called_once_with()

    def test_oauth_is_default_even_with_existing_runtime(self):
        with patch.object(onboard, "authenticate_clickup") as cup, \
             patch.object(onboard, "authenticate_github") as gh:
            onboard.run_onboarding(Path("/missing/ignored/runtime"))
        cup.assert_not_called()
        gh.assert_called_once_with()

    def test_cli_mode_fails_when_runtime_missing(self):
        with self.assertRaisesRegex(ValueError, "requires an installed runtime"):
            onboard.run_onboarding(None, mode="cli")


if __name__ == "__main__":
    unittest.main()
