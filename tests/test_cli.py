from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pygenesis.cli import main


def test_new_command_creates_minimal_project(tmp_path):
    output = StringIO()
    with redirect_stdout(output):
        exit_code = main(["new", "hello-world"], cwd=tmp_path)

    assert exit_code == 0
    assert "Project created successfully." in output.getvalue()

    project_dir = tmp_path / "hello-world"
    assert project_dir.is_dir()
    assert (project_dir / "pyproject.toml").exists()
    assert (project_dir / "README.md").exists()
    assert (project_dir / "src" / "hello_world").is_dir()
    assert (project_dir / "src" / "hello_world" / "__init__.py").exists()
    assert (project_dir / "src" / "hello_world" / "cli.py").exists()
    assert (project_dir / "tests").is_dir()
