from __future__ import annotations

import shutil
from pathlib import Path


class FileUtils:
    @staticmethod
    def ensure_dir(path: str | Path) -> Path:
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @staticmethod
    def write_file(path: str | Path, content: str) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return p

    @staticmethod
    def remove_tree(path: str | Path) -> None:
        p = Path(path)
        if p.exists():
            shutil.rmtree(p)

    @staticmethod
    def copy_tree(src: str | Path, dst: str | Path) -> None:
        shutil.copytree(Path(src), Path(dst), dirs_exist_ok=True)
