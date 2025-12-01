# evefit_core/skills.py

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from evefit_core.fit_models import SkillProfile

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SKILLS_DIR = DATA_DIR / "skills"
SKILLS_DIR.mkdir(parents=True, exist_ok=True)


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

        # Ensure all levels are ints
        clean_skills = {}
        for k, v in skills.items():
            try:
                clean_skills[str(k)] = int(v)
            except (TypeError, ValueError):
                continue

        profiles.append(SkillProfile(name=name, skills=clean_skills))

    if not profiles:
        # Fallback profile if user hasn't defined anything yet
        profiles.append(SkillProfile(name="No skills (dummy)", skills={}))

    return profiles


def save_skill_profile(profile: SkillProfile) -> None:
    """
    Save a single profile to data/skills/<name>.json.
    """
    from_slug = profile.name.strip().replace(" ", "_")
    filename = f"{from_slug}.json"
    path = SKILLS_DIR / filename

    data = asdict(profile)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
