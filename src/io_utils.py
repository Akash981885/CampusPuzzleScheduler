from __future__ import annotations

import json
from pathlib import Path

from src.models import Problem, load_problem


def read_problem(path: str | Path) -> Problem:
    with Path(path).open("r", encoding="utf-8") as handle:
        return load_problem(json.load(handle))
