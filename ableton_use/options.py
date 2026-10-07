"""Named choices in song.py that can be switched from outside — for comparing candidates.

    from ableton_use import option
    HAT_VEL = option("hatvel", 80)                 # the default is what the song uses
    BASS = option("bass", "muted")                 # ... if option("bass", ...) == "reese": ...

`ableton-use ab <project> hatvel=35 hatvel=60 --bars 81-84 --tracks Hats` builds, renders (or pushes to Live
and captures) each candidate and prints them side by side; `ableton-use --set hatvel=35 <command> ...`
runs any single command with a choice switched. Without either, every command uses the defaults.
"""
from __future__ import annotations

import json
import os
from contextlib import contextmanager
from typing import TypeVar

ENV = "ABLETON_USE_OPTIONS"
T = TypeVar("T")
_declared: dict[str, dict] = {}


def active() -> dict[str, str]:
    """The choices switched for this run: {name: value as text}."""
    raw = os.environ.get(ENV)
    return {str(k): str(v) for k, v in json.loads(raw).items()} if raw else {}


def _coerce(raw: str, default):
    if isinstance(default, bool):
        return raw.strip().lower() in ("1", "true", "yes", "on")
    if isinstance(default, int):
        return int(float(raw))
    if isinstance(default, float):
        return float(raw)
    return raw


def option(name: str, default: T) -> T:
    """The value of a named choice: `default`, unless this run switches it. A switched value is converted
    to the type of the default (number, True/False or text)."""
    raw = active().get(name)
    value = default if raw is None else _coerce(raw, default)
    _declared[name] = {"default": default, "value": value}
    return value  # type: ignore[return-value]


def begin() -> None:
    _declared.clear()


def declared() -> dict[str, dict]:
    return {k: dict(v) for k, v in _declared.items()}


def unknown() -> list[str]:
    """Switched names that song.py never asked for (a typo would otherwise silently do nothing)."""
    return [k for k in active() if k not in _declared]


def parse(pairs: list[str]) -> dict[str, str]:
    """['hatvel=35', 'wide=pan'] -> {'hatvel': '35', 'wide': 'pan'}"""
    out = {}
    for kv in pairs:
        for one in kv.split(","):
            k, eq, v = one.partition("=")
            if not eq or not k.strip():
                raise ValueError(f"expected name=value, got {one!r}")
            out[k.strip()] = v.strip()
    return out


@contextmanager
def using(values: dict[str, str] | None):
    """Run a block with these choices switched (replacing whatever was switched before)."""
    old = os.environ.get(ENV)
    if values:
        os.environ[ENV] = json.dumps(values)
    else:
        os.environ.pop(ENV, None)
    try:
        yield
    finally:
        if old is None:
            os.environ.pop(ENV, None)
        else:
            os.environ[ENV] = old
