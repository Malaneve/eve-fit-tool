# evefit_core/skills.py

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Dict

from evefit_core.fit_models import SkillProfile

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SKILLS_DIR = DATA_DIR / "skills"
SKILLS_DIR.mkdir(parents=True, exist_ok=True)


def _slugify_name(name: str) -> str:
    slug = name.strip().replace(" ", "_")
    return slug or "profile"


def load_skill_profiles() -> List[SkillProfile]:
    """
    Load all skill profiles from JSON files in data/skills.

    Each file should look like:

        {
          "name": "Malaneve",
          "skills": {
            "Gunnery": 4,
            "Small Hybrid Turret": 5
          }
        }

    If no files exist, we return a single "No skills" profile.
    """
    profiles: List[SkillProfile] = []

    for path in sorted(SKILLS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        name = data.get("name") or path.stem
        skills = data.get("skills") or {}

        if not isinstance(skills, dict):
            skills = {}

        clean_skills: Dict[str, int] = {}
        for k, v in skills.items():
            try:
                clean_skills[str(k)] = int(v)
            except (TypeError, ValueError):
                continue

        profiles.append(SkillProfile(name=name, skills=clean_skills))

    if not profiles:
        profiles.append(SkillProfile(name="No skills (dummy)", skills={}))

    return profiles


def save_skill_profile(profile: SkillProfile) -> None:
    """
    Save a single profile to data/skills/<slug>.json.
    """
    slug = _slugify_name(profile.name)
    filename = f"{slug}.json"
    path = SKILLS_DIR / filename

    data = asdict(profile)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def delete_skill_profile(name: str) -> None:
    """
    Delete the JSON file corresponding to the given profile name, if it exists.
    """
    slug = _slugify_name(name)
    path = SKILLS_DIR / f"{slug}.json"
    if path.exists():
        path.unlink()


def rename_skill_profile(old_name: str, new_name: str) -> None:
    """
    Rename a profile's file (and its internal "name" field).

    If the old file doesn't exist, this is a no-op.
    If the new file exists, it will be overwritten.
    """
    old_slug = _slugify_name(old_name)
    new_slug = _slugify_name(new_name)

    old_path = SKILLS_DIR / f"{old_slug}.json"
    new_path = SKILLS_DIR / f"{new_slug}.json"

    if not old_path.exists():
        return

    try:
        data = json.loads(old_path.read_text(encoding="utf-8"))
    except Exception:
        data = {}

    data["name"] = new_name

    new_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    if old_path != new_path and old_path.exists():
        old_path.unlink()
