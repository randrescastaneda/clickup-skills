"""Persistent entry point, independent of the npx cache and the caller's Python PATH."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
metadata = json.loads((ROOT / "runtime.json").read_text(encoding="utf-8"))
os.environ["CU_WORK_CUP_COMMAND"] = json.dumps(metadata["cup_command"])
if sys.argv[1:2] == ["--cup"]:
    raise SystemExit(subprocess.call(metadata["cup_command"] + sys.argv[2:]))
from clickup_skills.cli import main
main()
