"""Cross-client contract and isolated installer tests, without any user settings."""

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest.mock import patch

from clickup_skills.clients import CONFIG_CLIENTS, render_config, skill_directory

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("skill_installer", ROOT / "scripts/install_skills.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class ClientContracts(unittest.TestCase):
    def profile(self, name="context"):
        return json.loads((ROOT / "profiles" / (name + ".json")).read_text(encoding="utf-8"))

    def test_all_clients_render_all_profiles_without_reading_secret_values(self):
        with patch.dict(os.environ, {"CLICKUP_API_KEY": "do-not-export-this-secret"}):
            for client in CONFIG_CLIENTS:
                for profile in ("default", "official", "context", "rest"):
                    text = render_config(client, self.profile(profile))
                    self.assertNotIn("do-not-export-this-secret", text)
                    data = tomllib.loads(text) if client == "codex" else json.loads(text)
                    key = {"codex": "mcp_servers", "vscode": "servers", "kilo": "mcp"}.get(client, "mcpServers")
                    self.assertIn("clickup_work", data[key])
                    self.assertIn("github", data[key])

    def test_vscode_uses_servers_and_vscode_environment_references(self):
        data = json.loads(render_config("vscode", self.profile()))
        self.assertNotIn("mcpServers", data)
        server = data["servers"]["clickup_context"]
        self.assertEqual(server["type"], "stdio")
        self.assertEqual(server["env"]["CLICKUP_API_KEY"], "${env:CLICKUP_API_KEY}")

    def test_kilo_uses_local_argv_remote_and_environment(self):
        data = json.loads(render_config("kilo", self.profile()))["mcp"]
        self.assertEqual(data["clickup_work"]["command"], ["cu-work", "mcp"])
        self.assertEqual(data["clickup_work"]["type"], "local")
        self.assertEqual(data["github"]["type"], "remote")
        server = data["clickup_context"]
        self.assertNotIn("args", server)
        self.assertEqual(server["environment"]["CLICKUP_API_KEY"], "{env:CLICKUP_API_KEY}")

    def test_copilot_and_posit_are_distinct_from_vscode_and_kilo(self):
        copilot = json.loads(render_config("copilot", self.profile("official")))["mcpServers"]
        self.assertEqual(copilot["clickup_work"]["type"], "local")
        self.assertEqual(copilot["clickup_work"]["command"], "cu-work")
        self.assertEqual(copilot["clickup_work"]["tools"], ["*"])
        posit = json.loads(render_config("posit", self.profile("official")))["mcpServers"]
        self.assertEqual(posit["clickup_work"]["command"], ["cu-work", "mcp"])
        self.assertEqual(posit["clickup_official"]["auth"], "oauth")

    def test_input_remains_canonical_and_command_paths_are_not_shell_split(self):
        config = self.profile()
        original = copy.deepcopy(config)
        config["mcpServers"]["clickup_work"]["command"] = "/Applications/Team Tools/cu-work"
        for client in CONFIG_CLIENTS:
            rendered = render_config(client, config)
            self.assertIn("/Applications/Team Tools/cu-work", rendered)
        self.assertEqual(config["mcpServers"]["clickup_context"], original["mcpServers"]["clickup_context"])

    def test_user_and_project_skill_locations(self):
        home = Path(tempfile.gettempdir()) / "isolated-home"
        project = Path(tempfile.gettempdir()) / "isolated-project"
        self.assertEqual(skill_directory("copilot", home=home), home / ".copilot/skills")
        self.assertEqual(skill_directory("copilot", project_dir=project), project.resolve() / ".github/skills")
        self.assertEqual(skill_directory("kilo", project_dir=project), project.resolve() / ".kilo/skills")
        self.assertEqual(skill_directory("claude", home=home), home / ".claude/skills")


class InstallerBehavior(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "plugin"
        for name in ("alpha", "beta"):
            folder = self.source / "skills" / name
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text("Skill " + name, encoding="utf-8")
        (self.source / "LICENSE").write_text("MIT notice", encoding="utf-8")
        self.dest = self.root / "installed"
        self.patcher = patch.object(installer, "ROOT", self.source)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.tmp.cleanup()

    def test_copy_install_is_repeatable_and_carries_license(self):
        installer.install(self.dest)
        installer.install(self.dest)
        self.assertFalse((self.dest / "alpha").is_symlink())
        self.assertEqual((self.dest / "alpha/LICENSE").read_text(encoding="utf-8"), "MIT notice")

    def test_collision_preflight_prevents_partial_installation(self):
        conflict = self.dest / "beta"
        conflict.mkdir(parents=True)
        (conflict / "SKILL.md").write_text("User's existing skill", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Refusing"):
            installer.install(self.dest)
        self.assertFalse((self.dest / "alpha").exists())

    def test_update_only_managed_unmodified_copies(self):
        installer.install(self.dest)
        (self.source / "skills/alpha/SKILL.md").write_text("Updated source", encoding="utf-8")
        installer.install(self.dest, update=True)
        self.assertEqual((self.dest / "alpha/SKILL.md").read_text(encoding="utf-8"), "Updated source")
        (self.dest / "alpha/SKILL.md").write_text("Local customization", encoding="utf-8")
        (self.source / "skills/alpha/SKILL.md").write_text("Another update", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "locally modified"):
            installer.install(self.dest, update=True)
        self.assertEqual((self.dest / "alpha/SKILL.md").read_text(encoding="utf-8"), "Local customization")

    def test_project_scope_requires_explicit_target(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/install_skills.py"), "--client", "copilot", "--scope", "project"],
                                capture_output=True, text=True, encoding="utf-8", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires --project-dir", result.stderr)


if __name__ == "__main__":
    unittest.main()
