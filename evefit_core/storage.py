from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from evefit_core.fit_models import Fit


# Data directory: "<project_root>/data"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

FITS_FILE = DATA_DIR / "fits.json"


def save_fits(fits: List[Fit]) -> None:
    """
    Save a list of Fit objects to JSON on disk.
    """
    data = [asdict(f) for f in fits]
    with FITS_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_fits() -> List[Fit]:
    """
    Load fits from JSON if it exists, otherwise return an empty list.
    """
    if not FITS_FILE.exists():
        return []

    try:
        with FITS_FILE.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError:
        # If file is corrupted, don't crash the app
        return []

    fits: List[Fit] = []
    for item in raw:
        try:
            fit = Fit(
                id=item["id"],
                name=item["name"],
                ship_type=item["ship_type"],
                eft_text=item["eft_text"],
            )
            fits.append(fit)
        except KeyError:
            # Skip malformed entries
            continue

    return fits
