#!/usr/bin/env python3
"""Produit jeedom-audit-vX.Y.Z.skill (archive zip) depuis le dossier jeedom-audit/.

Usage:
    python build/package_skill.py [--version X.Y.Z] [--output DIR]

Sans --version, lit la version dans pyproject.toml.
Sans --output, produit le fichier dans dist/.
"""

import argparse
import re
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = REPO_ROOT / "jeedom-audit"
DIST_DIR = REPO_ROOT / "dist"

EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".DS_Store",
    "*.egg-info",
]


def read_version_from_pyproject() -> str:
    pyproject = REPO_ROOT / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        raise ValueError("Version introuvable dans pyproject.toml")
    return m.group(1)


def should_exclude(path: Path) -> bool:
    for part in path.parts:
        if part == "__pycache__":
            return True
        if part.endswith(".pyc") or part.endswith(".pyo"):
            return True
        if part == ".DS_Store":
            return True
    return False


def build_skill(version: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_file = output_dir / f"jeedom-audit-v{version}.skill"

    if not SKILL_DIR.exists():
        print(f"Erreur : dossier skill introuvable : {SKILL_DIR}", file=sys.stderr)
        sys.exit(1)

    files = sorted(
        p for p in SKILL_DIR.rglob("*") if p.is_file() and not should_exclude(p)
    )

    with zipfile.ZipFile(skill_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            arcname = f.relative_to(SKILL_DIR.parent)
            zf.write(f, arcname)

    total = sum(f.stat().st_size for f in files)
    print(f"Packaging : {len(files)} fichiers ({total / 1024:.1f} Ko)")
    print(f"Skill produite : {skill_file}")
    return skill_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", help="Version à packager (ex. 1.0.0)")
    parser.add_argument(
        "--output", type=Path, default=DIST_DIR, help="Répertoire de sortie"
    )
    args = parser.parse_args()

    version = args.version or read_version_from_pyproject()
    build_skill(version, args.output)


if __name__ == "__main__":
    main()
