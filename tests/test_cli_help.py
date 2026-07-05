from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_help_lists_new_and_version_commands():
    result = subprocess.run(
        [sys.executable, "-m", "pygenesis.cli", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")},
    )

    assert result.returncode == 0
    assert "new" in result.stdout
    assert "version" in result.stdout
