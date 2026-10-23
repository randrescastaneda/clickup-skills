"""Install behavior with isolated homes and an offline npm fixture; no account access."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tarfile
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("setup_installer", ROOT / "scripts/setup.py")
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class ConfigMergeTests(unittest.TestCase):
    def desired(self, client="kilo", runtime="first-runtime"):
        return setup.desired_config(client, "default", Path(tempfile.gettempdir()) / runtime)

    def test_jsonc_comments_trailing_commas_and_unrelated_settings_survive(self):
        original = '{ // team settings\n"model":"x", "mcp": {"other":{"url":"https://example.test/a//b"}, // keep\n},\n}'
        merged, owned = setup.merge_config(original, "kilo", self.desired(), {})
        self.assertIn("// team settings", merged)
        self.assertIn("// keep", merged)
        data = json.loads(setup.jsonc_text(merged))
        self.assertEqual(data["model"], "x")
        self.assertEqual(data["mcp"]["other"]["url"], "https://example.test/a//b")
        self.assertEqual(set(owned), {"clickup_work", "github"})
        repeated, _ = setup.merge_config(merged, "kilo", self.desired(), owned)
        self.assertEqual(repeated, merged)

    def test_update_managed_command_preserves_unrelated_servers(self):
        first, receipt = setup.merge_config('{"mcp":{"other":{"type":"remote","url":"x"}}}', "kilo", self.desired(), {})
        updated, _ = setup.merge_config(first, "kilo", self.desired(runtime="second-runtime"), receipt)
        self.assertIn("second-runtime", updated)
        self.assertEqual(json.loads(updated)["mcp"]["other"]["url"], "x")
        edited = updated.replace("second-runtime", "local-edit")
        with self.assertRaisesRegex(ValueError, "locally modified"):
            setup.merge_config(edited, "kilo", self.desired(), receipt)

    def test_unmanaged_work_server_is_not_replaced_but_known_legacy_config_migrates(self):
        with self.assertRaisesRegex(ValueError, "Refusing"):
            setup.merge_config('{"mcp":{"clickup_work":{"command":["custom"]}}}', "kilo", self.desired(), {})
        text = '{"mcp":{"clickup_work":{"type":"local","command":["cu-work","mcp"]}}}'
        migrated, owned = setup.merge_config(text, "kilo", self.desired(), {})
        self.assertIn("clickup_work", owned)
        self.assertNotIn('"cu-work"', migrated)

    def test_toml_preserves_personal_config_and_rejects_local_changes(self):
        original = '# keep my model\nmodel = "team-model"\n[mcp_servers.other]\nurl = "https://example.test"\n'
        first, receipt = setup.merge_config(original, "codex", self.desired("codex"), {})
        self.assertTrue(first.startswith(original))
        second, owned = setup.merge_config(first, "codex", self.desired("codex", "second-runtime"), receipt)
        self.assertTrue(second.startswith(original))
        self.assertEqual(len(tomllib.loads(second)["mcp_servers"]), 3)
        with self.assertRaisesRegex(ValueError, "locally modified"):
            setup.merge_config(second.replace('args = [', 'extra = true\nargs = [', 1), "codex", self.desired("codex"), owned)

    def test_toml_migrates_the_exact_legacy_renderer_without_duplicate_tables(self):
        original = setup.render_config("codex", {"mcpServers": {"clickup_work": {"type": "stdio", "command": "cu-work", "args": ["mcp"]}}})
        merged, _ = setup.merge_config(original, "codex", self.desired("codex"), {})
        self.assertEqual(tomllib.loads(merged), self.desired("codex"))

    def test_managed_backend_uses_argv_without_shell_interpretation(self):
        from clickup_skills.backends import ClickUp
        from clickup_skills.context import WorkError
        from types import SimpleNamespace
        context = SimpleNamespace(config={"routing": {}}, root=self.__class__.__name__)
        argv = ["/path with spaces/node", "/path with spaces/cup.js"]
        with patch.dict(os.environ, {"CU_WORK_CUP_COMMAND": json.dumps(argv)}), patch("clickup_skills.backends.execute", return_value={}) as execute:
            ClickUp(context).cup(["task", "safe;not-a-command"])
            execute.assert_called_once_with(argv + ["--json", "task", "safe;not-a-command"], context.root)
        with patch.dict(os.environ, {"CU_WORK_CUP_COMMAND": '"bad command"'}):
            with self.assertRaises(WorkError):
                ClickUp(context).cup([])

    def test_all_json_clients_and_existing_github_are_preserved(self):
        for client, key in (("claude", "mcpServers"), ("copilot", "mcpServers"), ("vscode", "servers"), ("kilo", "mcp")):
            text = json.dumps({key: {"github": {"url": "https://my-own-github.test"}}, "other_setting": True})
            merged, owned = setup.merge_config(text, client, self.desired(client), {})
            self.assertTrue(json.loads(merged)["other_setting"])
            self.assertEqual(json.loads(merged)[key]["github"]["url"], "https://my-own-github.test")
            self.assertNotIn("github", owned)

    def test_renamed_github_server_is_reused_and_ambiguous_json_is_rejected(self):
        text = '{"mcp":{"team_github":{"url":"https://api.githubcopilot.com/mcp/"}}}'
        merged, owned = setup.merge_config(text, "kilo", self.desired(), {})
        self.assertNotIn("github", owned)
        self.assertEqual(set(json.loads(merged)["mcp"]), {"team_github", "clickup_work"})
        with self.assertRaises(ValueError):
            setup.merge_config('{"mcp":{},"mcp":{}}', "kilo", self.desired(), {})


class HostedOAuthSetupTests(unittest.TestCase):
    def setUp(self):
        from types import SimpleNamespace
        self.temporary = tempfile.TemporaryDirectory(prefix="clickup oauth setup ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.settings = self.root / "kilo.jsonc"
        self.skills = self.root / ".kilo/skills"
        self.home = self.root / "managed"
        self.args = SimpleNamespace(client="kilo", profile="default",
                                    project_dir=None, skip_skills=False)

    def run_host(self):
        with patch.object(setup, "config_destination", return_value=self.settings), \
             patch.object(setup, "skill_directory", return_value=self.skills):
            setup.setup_host(self.args, self.home)

    def test_oauth_install_has_no_cli_runtime_or_personal_credentials(self):
        self.settings.write_text('{ // preserve\n"model":"my-model",\n"mcp": {},\n}', encoding="utf-8")
        self.run_host()
        config_text = self.settings.read_text(encoding="utf-8")
        config = json.loads(setup.jsonc_text(config_text))
        self.assertIn("// preserve", config_text)
        self.assertEqual(config["model"], "my-model")
        self.assertEqual(set(config["mcp"]), {"clickup_official", "github"})
        self.assertEqual(config["mcp"]["clickup_official"]["url"],
                         "https://mcp.clickup.com/mcp")
        self.assertFalse((self.home / "releases").exists())
        self.assertFalse((self.home / "installation.json").exists())
        self.assertEqual(len(list(self.skills.glob("*/SKILL.md"))), 6)
        self.assertNotIn("clickup_work", config["mcp"])
        self.assertEqual(len(list(self.settings.parent.glob("*.clickup-skills-backup-*"))), 1)
        self.run_host()
        self.assertEqual(self.settings.read_text(encoding="utf-8"), config_text)

    def test_existing_remote_and_local_helper_are_preserved(self):
        existing = {
            "mcp": {
                "clickup_official": {"type": "remote", "url": "https://mcp.clickup.com/mcp", "enabled": True},
                "clickup_work": {"type": "local", "command": ["/private/python", "script.py", "mcp"]},
                "github": {"type": "remote", "url": "https://hosted.example/github", "enabled": True},
            },
            "permissions": {"clickup_official_*": "ask"}
        }
        self.settings.write_text(json.dumps(existing), encoding="utf-8")
        self.run_host()
        after = json.loads(self.settings.read_text(encoding="utf-8"))
        self.assertEqual(after, existing)
        self.assertFalse((self.home / "releases").exists())

    def test_host_only_keeps_vercel_managed_skills_unchanged(self):
        first = self.skills / "clickup-route/SKILL.md"
        first.parent.mkdir(parents=True)
        first.write_text("Vercel-owned", encoding="utf-8")
        self.args.skip_skills = True
        self.run_host()
        self.assertEqual(first.read_text(encoding="utf-8"), "Vercel-owned")
        self.assertEqual(len(list(self.skills.glob("*/SKILL.md"))), 1)
        self.assertTrue(self.settings.exists())

    def test_conflicting_named_oauth_server_fails_closed(self):
        original = '{"mcp":{"clickup_official": {"type":"remote","url":"https://evil.example/mcp"}}}'
        self.settings.write_text(original, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not the expected browser-OAuth MCP"):
            self.run_host()
        self.assertEqual(self.settings.read_text(encoding="utf-8"), original)
        self.assertFalse(self.home.exists())
        self.assertFalse(self.skills.exists())

    def test_disabled_or_token_header_oauth_server_is_rejected(self):
        for extra in ({"enabled": False}, {"oauth": False}, {"headers": {"Authorization": "Bearer old"}}):
            self.settings.write_text(json.dumps({"mcp": {"clickup_official": {
                "type": "remote", "url": "https://mcp.clickup.com/mcp", **extra
            }}}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not the expected browser-OAuth MCP"):
                self.run_host()

    def test_unsupported_host_profile_fails_without_changes(self):
        self.args.profile = "context"
        with self.assertRaisesRegex(ValueError, "only the official"):
            self.run_host()
        self.assertFalse(self.settings.exists())
        self.assertFalse(self.home.exists())

    def test_oauth_client_config_is_valid_for_all_installer_targets(self):
        for client, key in (("kilo", "mcp"), ("codex", "mcp_servers"),
                            ("claude", "mcpServers"), ("copilot", "mcpServers"),
                            ("vscode", "servers")):
            config = setup.desired_host_config(client)
            self.assertEqual(set(config[key]), {"clickup_official", "github"})
            self.assertNotIn("clickup_work", config[key])

    def test_mode_defaults_oauth_and_cli_is_explicit(self):
        import onboard
        with patch.object(sys, "argv", ["setup.py", "onboard", "--client", "kilo"]), \
             patch.object(setup, "setup_host") as host, \
             patch.object(setup, "setup") as local, \
             patch.object(onboard, "run_onboarding") as auth:
            setup.main()
        host.assert_called_once()
        local.assert_not_called()
        auth.assert_called_once_with(None, mode="oauth")

        with patch.object(sys, "argv", ["setup.py", "onboard", "--client", "kilo", "--mode", "cli"]), \
             patch.object(setup, "setup_host") as host, \
             patch.object(setup, "setup") as local, \
             patch.object(setup, "read_json", return_value={"runtime": "/test/runtime"}), \
             patch.object(onboard, "run_onboarding") as auth:
            setup.main()
        host.assert_not_called()
        local.assert_called_once()
        auth.assert_called_once_with(Path("/test/runtime"), mode="cli")


class PackagedInstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="clickup setup ")
        self.root = Path(self.temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.managed = self.home / "managed tools"
        self.project = self.root / "project"
        self.project.mkdir()
        self.env = {**os.environ, "HOME": str(self.home), "USERPROFILE": str(self.home),
                    "CLICKUP_SKILLS_HOME": str(self.managed), "CLICKUP_SKILLS_NODE": shutil.which("node"),
                    "CLICKUP_SKILLS_NPM_CLI": str(ROOT / "tests/fixtures/fake_npm_cli.cjs")}

    def tearDown(self):
        self.temporary.cleanup()

    def run_setup(self, command="setup", check=True, extra_env=None):
        return subprocess.run([sys.executable, "-I", str(ROOT / "scripts/setup.py"), command, "--client", "kilo",
                               "--project-dir", str(self.project)], env={**self.env, **(extra_env or {})},
                              capture_output=True, text=True, encoding="utf-8", check=check)

    def test_setup_repeat_and_update_without_global_install_or_activation(self):
        settings = self.project / ".kilo/kilo.jsonc"
        settings.parent.mkdir()
        settings.write_text('{ // preserve\n"model":"personal",\n}', encoding="utf-8")
        self.run_setup()
        first = settings.read_text(encoding="utf-8")
        runtime = Path(json.loads((self.managed / "installation.json").read_text())["runtime"])
        metadata = json.loads((runtime / "runtime.json").read_text())
        self.assertEqual(metadata["cup_version"], "9.0.0-test")
        self.assertIn("// preserve", first)
        self.assertEqual(len(list(self.project.glob(".kilo/skills/*/SKILL.md"))), 6)
        self.assertEqual(len(list(settings.parent.glob("*.clickup-skills-backup-*"))), 1)
        self.run_setup()
        self.assertEqual(settings.read_text(), first)
        self.assertEqual(len(list((self.managed / "releases").iterdir())), 1)
        # This command references only the persistent environment, never an npx cache.
        argv = json.loads(setup.jsonc_text(first))["mcp"]["clickup_work"]["command"]
        result = subprocess.run(argv[:-1] + ["--help"], env=self.env, capture_output=True, text=True, check=True)
        self.assertIn("task-scoped", result.stdout)
        self.run_setup("update")
        self.assertNotEqual(settings.read_text(), first)
        self.assertEqual(len(list((self.managed / "releases").iterdir())), 2)
        cup = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/setup.py"), "cup", "--version"],
                             env=self.env, capture_output=True, text=True, check=True)
        self.assertIn("9.0.0-test", cup.stdout)

    def test_skip_skills_preserves_external_installation(self):
        skill = self.project / '.kilo/skills/clickup-route/SKILL.md'
        skill.parent.mkdir(parents=True)
        skill.write_text('Vercel-managed independent copy', encoding='utf-8')
        result = subprocess.run(
            [sys.executable, '-I', str(ROOT / 'scripts/setup.py'), 'setup', '--client', 'kilo',
             '--project-dir', str(self.project), '--skip-skills'],
            env=self.env, capture_output=True, text=True, encoding='utf-8', check=True)
        self.assertIn('external skills unchanged', result.stdout)
        self.assertEqual(skill.read_text(encoding='utf-8'), 'Vercel-managed independent copy')
        self.assertFalse((self.project / '.kilo/skills/clickup-github').exists())
        self.assertTrue((self.project / '.kilo/kilo.jsonc').is_file())
        result = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts/setup.py'), 'update',
                '--client', 'kilo', '--project-dir', str(self.project), '--skip-skills'],
                env=self.env, capture_output=True, text=True, encoding='utf-8', check=True)
        self.assertEqual(skill.read_text(encoding='utf-8'), 'Vercel-managed independent copy')

    def test_failed_dependency_install_does_not_change_settings_or_skills(self):
        settings = self.project / ".kilo/kilo.jsonc"
        settings.parent.mkdir()
        settings.write_text('{"model":"personal"}', encoding="utf-8")
        result = self.run_setup(check=False, extra_env={"TEST_NPM_FAIL": "1"})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(settings.read_text(), '{"model":"personal"}')
        self.assertFalse((self.project / ".kilo/skills").exists())
        self.assertFalse((self.managed / "installation.json").exists())
        self.assertEqual(list((self.managed / "releases").iterdir()), [])

    def test_skill_conflict_is_detected_before_any_dependency_install(self):
        skill = self.project / ".kilo/skills/clickup-route/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("My custom skill", encoding="utf-8")
        result = self.run_setup(check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing", result.stderr)
        self.assertFalse(self.managed.exists())

    def test_node_bootstrap_has_no_side_effects_for_help(self):
        result = subprocess.run([shutil.which("node"), str(ROOT / "bin/clickup-skills.mjs"), "--help"],
                                env=self.env, capture_output=True, text=True, check=True)
        self.assertIn("--client", result.stdout)
        self.assertFalse(self.managed.exists())

    def test_npm_archive_contains_the_runtime_and_installs_after_unpacking(self):
        npm = Path(shutil.which("npm"))
        cli = npm.resolve() if os.name != "nt" else npm.parent / "node_modules/npm/bin/npm-cli.js"
        result = subprocess.run([shutil.which("node"), str(cli), "pack", "--ignore-scripts", "--json", "--pack-destination", str(self.root)],
                                cwd=ROOT, capture_output=True, text=True, check=True)
        packed = json.loads(result.stdout)[0]
        names = {item["path"] for item in packed["files"]}
        self.assertIn("bin/clickup-skills.mjs", names)
        self.assertIn("scripts/setup.py", names)
        self.assertIn("scripts/onboard.py", names)
        self.assertIn("scripts/run_work.py", names)
        self.assertIn("profiles/default.json", names)
        self.assertIn("third_party/krodak/LICENSE", names)
        self.assertEqual(len([n for n in names if n.startswith("skills/") and n.endswith("/SKILL.md")]), 6)
        self.assertFalse(any("__pycache__" in n or n.startswith(("tests/", ".git/")) or n.endswith(".pyc") for n in names))
        unpacked = self.root / "downloaded"
        with tarfile.open(self.root / packed["filename"]) as archive:
            archive.extractall(unpacked, filter="data")
        script = unpacked / "package/scripts/setup.py"
        subprocess.run([sys.executable, "-I", str(script), "setup", "--client", "kilo", "--project-dir", str(self.project)],
                       env=self.env, capture_output=True, text=True, check=True)
        # Delete the downloaded source: the configured MCP must still initialize and list tools.
        shutil.rmtree(unpacked)
        settings = self.project / ".kilo/kilo.jsonc"
        argv = json.loads(settings.read_text())["mcp"]["clickup_work"]["command"]
        messages = '\n'.join(json.dumps(m) for m in [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        ]) + '\n'
        result = subprocess.run(argv, input=messages, env=self.env, capture_output=True, text=True, check=True)
        responses = [json.loads(line) for line in result.stdout.splitlines()]
        tools = next(r["result"]["tools"] for r in responses if r.get("id") == 2)
        self.assertEqual(len(tools), 9)
        help_result = subprocess.run(argv[:-1] + ["sync-worker", "--help"], env=self.env,
                                     capture_output=True, text=True, check=True)
        self.assertIn("--max-writes", help_result.stdout)
        self.assertIn("--apply", help_result.stdout)


if __name__ == "__main__":
    unittest.main()
