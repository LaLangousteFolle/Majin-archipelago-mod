"""Game memory addresses, loaded from majin_addresses.json (edit it, or let memdiff.py write it).

Everything is addressed as base + address. Numbers in the JSON can be ints or hex strings ("0x2BCA16D40").

Example majin_addresses.json:
{
  "base": 0,
  "xp": "0x2BCA16D40",
  "xp_per_life_shards": 50,
  "goal_flag": {"address": "0x2BCA10123", "mask": "0x01"},
  "location_flags": {
    "Graveyard - Life Chest 1": {"address": "0x2BCA10000", "mask": "0x04"},
    "Caprakan Defeated": {"address": "0x2BCA10010", "mask": "0x01", "invert": true}
  },
  "item_effects": {
    "Stamina Fruit": {"kind": "add", "address": "0x2BCA10200", "size": 4, "amount": 1}
  }
}
Flag: the location is checked when (byte(s) at address & mask) != 0 (== 0 when "invert" is true).
ItemEffect kind: "add" (value += amount), "set" (value = amount), "or" (value |= amount, for bit flags).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

from .. import data

# Experience of the human character, verified with Cheat Engine on Xenia (Linux/Wine), stable across restarts.
# The game only refreshes the displayed value after an enemy kill + XP pickup.
DEFAULT_XP_ADDRESS = 0x2BCA16D40
# Experience granted by one "Life Shards (XP)" item. To be tuned in game.
DEFAULT_XP_PER_LIFE_SHARDS = 50

VALID_SIZES = (1, 2, 4)
VALID_KINDS = ("add", "set", "or")


@dataclass(frozen=True)
class Flag:
    """A location is checked when (value at address) & mask is non-zero (zero if invert)."""

    address: int
    mask: int = 0x1
    size: int = 1
    invert: bool = False


@dataclass(frozen=True)
class ItemEffect:
    """What receiving an item does to memory."""

    kind: str
    address: int
    size: int = 4
    amount: int = 1


@dataclass
class AddressTable:
    base: int = 0
    xp: int | None = DEFAULT_XP_ADDRESS
    location_flags: dict[str, Flag] = field(default_factory=dict)
    item_effects: dict[str, ItemEffect] = field(default_factory=dict)
    goal_flag: Flag | None = None  # final boss beaten
    source: str = "built-in defaults"

    def summary(self) -> str:
        return (f"{len(self.location_flags)}/{len(data.LOCATIONS)} location flags, "
                f"{len(self.item_effects)} item effects, goal flag {'set' if self.goal_flag else 'MISSING'} "
                f"({self.source})")


def _xp_effect(xp: int | None, per_shard: int) -> dict[str, ItemEffect]:
    return {data.XP_ITEM: ItemEffect("add", xp, 4, per_shard)} if xp is not None else {}


def default_table() -> AddressTable:
    return AddressTable(item_effects=_xp_effect(DEFAULT_XP_ADDRESS, DEFAULT_XP_PER_LIFE_SHARDS))


def fake_table() -> AddressTable:
    """A synthetic memory layout covering every location and item, for testing without the game."""
    location_flags = {loc.name: Flag(0x1000 + 4 * i) for i, loc in enumerate(data.LOCATIONS)}
    item_effects = _xp_effect(0x10, DEFAULT_XP_PER_LIFE_SHARDS)
    for i, name in enumerate([*data.FRUIT_ITEMS, *data.COSTUME_ITEMS, *data.POWERS.values()]):
        item_effects[name] = ItemEffect("add", 0x100 + 4 * i, 4, 1)
    return AddressTable(0, 0x10, location_flags, item_effects, Flag(0x20), "fake memory layout")


# --- JSON loading ------------------------------------------------------------------------------------------
def _num(value: Any, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError(f"{what}: expected a number, got {value!r}")
    try:
        return int(value, 0) if isinstance(value, str) else value
    except ValueError:
        raise ValueError(f"{what}: {value!r} is not a number") from None


def _parse_flag(raw: Any, what: str) -> Flag:
    if not isinstance(raw, dict) or "address" not in raw:
        raise ValueError(f"{what}: expected an object with an 'address'")
    size = _num(raw.get("size", 1), f"{what}.size")
    mask = _num(raw.get("mask", 1), f"{what}.mask")
    if size not in VALID_SIZES:
        raise ValueError(f"{what}: size must be one of {VALID_SIZES}")
    if not 0 < mask < (1 << (8 * size)):
        raise ValueError(f"{what}: mask {mask:#x} does not fit in {size} byte(s)")
    return Flag(_num(raw["address"], f"{what}.address"), mask, size, bool(raw.get("invert", False)))


def _parse_effect(raw: Any, what: str) -> ItemEffect:
    if not isinstance(raw, dict) or "address" not in raw:
        raise ValueError(f"{what}: expected an object with an 'address'")
    kind = raw.get("kind", "add")
    size = _num(raw.get("size", 4), f"{what}.size")
    if kind not in VALID_KINDS:
        raise ValueError(f"{what}: kind must be one of {VALID_KINDS}")
    if size not in VALID_SIZES:
        raise ValueError(f"{what}: size must be one of {VALID_SIZES}")
    return ItemEffect(kind, _num(raw["address"], f"{what}.address"), size, _num(raw.get("amount", 1), f"{what}.amount"))


def load_table(path: str | None) -> tuple[AddressTable, list[str]]:
    """Built-in defaults overridden by the JSON file. Returns (table, warnings); never raises on bad content."""
    table = default_table()
    warnings: list[str] = []
    if not path or not os.path.exists(path):
        return table, [f"no address file found ({path}): only the XP address is known"]
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, dict):
            raise ValueError("the top level must be an object")
    except (OSError, ValueError) as e:
        return table, [f"cannot read {path}: {e}"]

    table.source = path
    known_keys = {"base", "xp", "xp_per_life_shards", "goal_flag", "location_flags", "item_effects"}
    for key in raw:
        if key not in known_keys and not key.startswith("_"):
            warnings.append(f"unknown key {key!r} ignored")

    def guarded(what: str, fn):
        try:
            return fn()
        except ValueError as e:
            warnings.append(str(e))
            return None

    if "base" in raw:
        table.base = guarded("base", lambda: _num(raw["base"], "base")) or 0
    if "xp" in raw:
        table.xp = guarded("xp", lambda: _num(raw["xp"], "xp"))
    per_shard = DEFAULT_XP_PER_LIFE_SHARDS
    if "xp_per_life_shards" in raw:
        per_shard = guarded("xp_per_life_shards", lambda: _num(raw["xp_per_life_shards"], "xp_per_life_shards")) \
            or DEFAULT_XP_PER_LIFE_SHARDS
    table.item_effects = _xp_effect(table.xp, per_shard)

    if "goal_flag" in raw:
        table.goal_flag = guarded("goal_flag", lambda: _parse_flag(raw["goal_flag"], "goal_flag"))

    for name, entry in (raw.get("location_flags") or {}).items():
        if name not in data.LOCATION_NAME_TO_ID:
            warnings.append(f"unknown location {name!r} ignored (typo?)")
            continue
        flag = guarded(name, lambda: _parse_flag(entry, name))
        if flag is not None:
            table.location_flags[name] = flag

    for name, entry in (raw.get("item_effects") or {}).items():
        if name not in data.ITEM_NAME_TO_ID:
            warnings.append(f"unknown item {name!r} ignored (typo?)")
            continue
        effect = guarded(name, lambda: _parse_effect(entry, name))
        if effect is not None:
            table.item_effects[name] = effect
    return table, warnings
