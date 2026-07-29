from __future__ import annotations

import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "permission-compiler" / "SKILL.md"


def parse_skill():
    text = SKILL.read_text(encoding="utf-8")
    assert text.startswith("---")
    end = text.find("\n---", 3)
    assert end > 0
    return yaml.safe_load(text[3:end].strip()), text[end + 4 :].lstrip("\n")


def test_skill_metadata_and_name():
    frontmatter, _ = parse_skill()
    name = frontmatter["name"]
    assert name == SKILL.parent.name
    assert len(name) <= 64
    assert re.fullmatch(r"[a-z0-9]([a-z0-9-]*[a-z0-9])?", name)
    assert 0 < len(frontmatter["description"]) <= 1024


def test_skill_body_and_references():
    _, body = parse_skill()
    assert len(body.splitlines()) <= 500
    references = re.findall(
        r"\[(?:[^\]]*)\]\((?!https?://)([^)#\s]+)", body
    )
    assert all((SKILL.parent / reference).resolve().exists() for reference in references)
