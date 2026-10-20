"""Behavioral regression checks for documentation decisions in plugin changes."""

import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("docs_impact", Path(__file__).resolve().parents[1] / "scripts/check_docs_impact.py")
impact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(impact)


class DocsImpactTests(unittest.TestCase):
    def test_behavior_change_needs_guide_decision(self):
        with self.assertRaisesRegex(ValueError, "src/clickup_skills/workflow.py"):
            impact.check(["src/clickup_skills/workflow.py", "site/assets/style.css"], {}, {})

    def test_relevant_guide_satisfies_behavior_change(self):
        impact.check(["skills/clickup-github/SKILL.md", "site/content/synchronization.md"], {}, {})

    def test_old_rationale_cannot_cover_a_new_change(self):
        record = {"paths": ["profiles/default.json"], "reason": "Only a generated server listing changes; no onboarding or workflow behavior changes for existing users."}
        with self.assertRaises(ValueError):
            impact.check(["profiles/default.json"], {"changes": [record]}, {"changes": [record]})

    def test_new_rationale_must_cover_all_behavior_paths(self):
        new = {"changes": [{"paths": ["profiles/default.json"], "reason": "Only a generated server listing changes; no onboarding or workflow behavior changes for existing users."}]}
        impact.check(["profiles/default.json"], {}, new)
        with self.assertRaisesRegex(ValueError, "src/clickup_skills/mcp.py"):
            impact.check(["profiles/default.json", "src/clickup_skills/mcp.py"], {}, new)

    def test_design_only_change_needs_no_behavior_exception(self):
        impact.check(["site/assets/style.css", "site/assets/favicon.svg"], {}, {})

    def test_short_or_missing_reason_rejected(self):
        with self.assertRaisesRegex(ValueError, "concrete reason"):
            impact.check(["plugin.json"], {}, {"changes": [{"paths": ["plugin.json"], "reason": "generated"}]})


if __name__ == "__main__":
    unittest.main()
