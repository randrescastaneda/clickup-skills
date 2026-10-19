"""Print (never overwrite) MCP configuration for a chosen client and profile."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from clickup_skills.clients import CONFIG_CLIENTS, render_config


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--client", choices=CONFIG_CLIENTS, required=True)
    p.add_argument("--profile", choices=["default", "official", "context", "rest"], default="default")
    a = p.parse_args()
    config = json.loads((ROOT / "profiles" / (a.profile + ".json")).read_text(encoding="utf-8"))
    print(render_config(a.client, config), end="")


if __name__ == "__main__":
    main()
