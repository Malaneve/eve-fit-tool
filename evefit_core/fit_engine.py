# evefit_core/fit_engine.py

from __future__ import annotations

from typing import List

from evefit_core.fit_models import Fit, SkillProfile, FitStats, EvaluatedFit


class FitEngine:
    """
    Simple, skill-aware fit engine.

    Right now this uses a deliberately simple formula:

    - Count modules (non-empty, non-header lines).
    - Sum all skill levels.
    - Use those as multipliers for some base numbers.

    The goal is NOT realism yet, but:
      - deterministic behavior,
      - visible effect of skills,
      - a clean API we can later wire to real EVE data / services.
    """

    def __init__(self) -> None:
        # In the future we might keep cache, ship data, etc. here.
        pass

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def evaluate_fit(self, fit: Fit, skills: SkillProfile) -> EvaluatedFit:
        """
        Calculate stats for the given fit + skill profile.
        """
        module_lines: List[str] = [
            ln.strip()
            for ln in fit.eft_text.splitlines()
            if ln.strip() and not ln.strip().startswith("[")
        ]
        module_count = len(module_lines)

        total_skill_levels = sum(level for level in skills.skills.values())

        # Base numbers
        base_ehp = 10_000.0
        base_dps = 50.0
        base_volley = 150.0

        # Simple scaling: modules and skills both matter
        ehp = base_ehp + module_count * 500.0 + total_skill_levels * 100.0
        dps = base_dps + module_count * 10.0 + total_skill_levels * 2.0
        volley = base_volley + dps * 2.0

        # Capacitor: just pretend everything is stable for now
        cap_stable = True
        cap_lasts_seconds = None

        # Dummy resists – flat profile
        resist_profile = {
            "EM": 70.0,
            "Therm": 60.0,
            "Kin": 55.0,
            "Expl": 50.0,
        }

        misc = {
            "modules": float(module_count),
            "skill_levels": float(total_skill_levels),
        }

        stats = FitStats(
            ehp=ehp,
            dps=dps,
            volley=volley,
            cap_stable=cap_stable,
            cap_lasts_seconds=cap_lasts_seconds,
            resist_profile=resist_profile,
            misc=misc,
        )

        return EvaluatedFit(fit=fit, stats=stats, skill_profile=skills)
