# evefit_core/fit_models.py

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class SkillProfile:
    """
    Represents a character's skills.

    Example:
        name = "Malaneve"
        skills = {
            "Gunnery": 4,
            "Small Hybrid Turret": 5,
        }
    """
    name: str
    skills: Dict[str, int]


@dataclass
class Fit:
    """
    A ship fit as seen by the app.

    eft_text contains the full EFT block:
        [Ship, Fit Name]
        ...
    """
    id: str
    name: str
    ship_type: str
    eft_text: str


@dataclass
class FitStats:
    """
    Simplified stats used by the GUI.

    These are currently calculated with a dummy formula, but the shape
    is future-proof so we can plug in real math or external services later.
    """
    ehp: float
    dps: float
    volley: float
    cap_stable: bool
    cap_lasts_seconds: Optional[float]
    resist_profile: Dict[str, float]
    misc: Dict[str, float]


@dataclass
class EvaluatedFit:
    """
    A fit together with its calculated stats and the skills used.
    """
    fit: Fit
    stats: FitStats
    skill_profile: SkillProfile
