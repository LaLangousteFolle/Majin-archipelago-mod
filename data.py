"""Static data for Majin and the Forsaken Kingdom.

Source of the collectibles: the Tyger7 collectible guide (XboxAchievements). The zone numbers are the
in-game map sections, in the order of that guide.

Requirement strings are sets of power letters: W = Wind, L = Lightning, F = Fire, P = Purification.
"" means the collectible needs nothing beyond reaching the zone.
"""
from __future__ import annotations

from typing import NamedTuple

GAME_NAME = "Majin and the Forsaken Kingdom"

LOCATION_BASE_ID = 8_120_000
ITEM_BASE_ID = 8_120_000

POWERS: dict[str, str] = {
    "W": "Wind Power",
    "L": "Lightning Power",
    "F": "Fire Power",
    "P": "Purification Power",
}

# Boss n is fought at the end of this zone. The next zone opens once it is beaten.
BOSS_ZONES: dict[int, int] = {1: 4, 2: 9, 3: 12, 4: 18}
# Powers are required cumulatively: boss n needs the first n powers (conservative, never softlocks).
BOSS_REQUIREMENTS: dict[int, str] = {1: "W", 2: "WL", 3: "WLF", 4: "WLFP"}
FINAL_ZONE = 21
FINAL_BOSS_REQUIREMENT = "WLFP"

# Where the story hands each power to the player (zone, area name).
# NOTE: the Purification spot is a best guess from the guide and has to be confirmed in game.
POWER_SPOTS: dict[str, tuple[int, str]] = {
    "W": (4, "Graveyard"),
    "L": (9, "Experimental Wing"),
    "F": (11, "Ravine Dig Site"),
    "P": (17, "Tanya Mafta City"),
}


class Area(NamedTuple):
    zone: int
    name: str
    life: tuple[str, ...] = ()
    memory: tuple[str, ...] = ()
    costume: tuple[tuple[str, str], ...] = ()  # (piece name or "", requirement)
    stamina: tuple[str, ...] = ()
    strength: tuple[str, ...] = ()
    upgrade: tuple[tuple[str, str], ...] = ()  # (power letter of the fruit, requirement)
    missable: bool = False


AREAS: list[Area] = [
    # Zone 1: first castle areas, cannot be revisited (the story stamina fruit is not a location)
    Area(1, "Underground Storehouse", life=("", ""), missable=True),
    Area(1, "Royal Chambers", life=("",), missable=True),
    Area(1, "Corridor", life=("",), missable=True),
    # Zone 2
    Area(2, "Arkela Castle Gate", life=("",), memory=("",)),
    Area(2, "Ungdo Flower Patch", life=("",), memory=("",), costume=(("Guard Knight's Gauntlets", ""),)),
    # Zone 3
    Area(3, "Tagalo Forest Checkpoint", life=("", ""), memory=("",), strength=("",)),
    Area(3, "Toto Waterfall Power Plant", life=("", ""), memory=("",), stamina=("",)),
    Area(3, "B'alam Laboratory", life=("", "L"), memory=("L",), costume=(("Bandit's Hood", "L"),),
         strength=("L",)),
    # Zone 4 (wind power, boss 1)
    Area(4, "Potrachi Altar", life=("", ""), memory=("",), costume=(("", ""),), strength=("",)),
    Area(4, "Graveyard", life=("", ""), memory=("",), costume=(("Guard Knight Armor", ""),), stamina=("",)),
    # Zone 5
    Area(5, "Excavation Site", life=("", ""), memory=("",)),
    # Zone 6
    Area(6, "Hawme'a Falls", life=("",), memory=("",)),
    Area(6, "Denguey Forest Tower", life=("", "", ""), memory=("",), strength=("",)),
    Area(6, "Pele Bridge", life=("", "F"), memory=("",),
         costume=(("Scholar's Hat", ""), ("Bandit's Manifer", "FL")), upgrade=(("F", "F"),)),
    Area(6, "Tangalo'a Swamp", life=("", ""), memory=("",), stamina=("L",), upgrade=(("W", "L"),)),
    # Zone 7
    Area(7, "Kanay Valley", life=("",), memory=("",), strength=("",)),
    Area(7, "Wana Mu'bi Fortress", life=("", ""), memory=("",), costume=(("Scholar's Cuff", ""),),
         stamina=("",)),
    # Zone 8
    Area(8, "Royal Garden", life=("", ""), memory=("",), upgrade=(("W", ""),)),
    # Zone 9 (lightning power, boss 2)
    Area(9, "Research Wing", life=("", ""), memory=("",), strength=("",)),
    Area(9, "Experimental Wing", life=("L", "L"), memory=("L",), costume=(("", "L"),), stamina=("L",)),
    # Zone 10
    Area(10, "Pualata Cargo Shed", life=("",), memory=("",)),
    Area(10, "Dudugera Way", life=("", ""), memory=("",), strength=("",)),
    # Zone 11 (fire power)
    Area(11, "Ravine Dig Site", life=("", "F"), memory=("F",), stamina=("F",), upgrade=(("L", "F"),)),
    Area(11, "Naval Equipment Warehouse", life=("", ""), memory=("",), costume=(("Marine's Manifer", ""),),
         upgrade=(("L", ""), ("F", "F"))),
    # Zone 12 (boss 3)
    Area(12, "Kingdom Navy Headquarters", life=("", ""), memory=("",), costume=(("Helm of Darkness", "F"),),
         stamina=("",)),
    Area(12, "Chibirias Stern", life=("", "", ""), memory=("",), costume=(("Marine's Uniform", ""),)),
    # Zone 13
    Area(13, "Iron Factory", life=("", "F"), memory=("",), costume=(("Bandit's Costume", ""),),
         upgrade=(("W", ""),)),
    Area(13, "Earth Furnace", life=("", ""), memory=("",), costume=(("Marine's Cap", ""),), strength=("",)),
    # Zone 14
    Area(14, "Chibirias Engine", life=("", ""), memory=("",), stamina=("",)),
    # Zone 15
    Area(15, "Koom Honu'a Passage", life=("",), memory=("",)),
    Area(15, "Moonglow Cave", life=("", ""), memory=("",), strength=("",)),
    # Zone 16
    Area(16, "Koonapipi Mines", life=("", ""), memory=("",), costume=(("Attendant's Decorative Sleeve", ""),),
         stamina=("",)),
    Area(16, "Four Windmills Hill", life=("", "", ""), memory=("",), upgrade=(("F", ""),)),
    # Zone 17 (purification power)
    Area(17, "Tanya Mafta City", life=("", ""), memory=("",), upgrade=(("L", ""),)),
    Area(17, "Tu Kabinana Residence", life=("", ""), memory=("",), costume=(("Attendant's Formal Cap", ""),),
         upgrade=(("P", "P"),)),
    # Zone 18 (boss 4)
    Area(18, "Crystal Palace Courtyard", life=("", ""), memory=("",),
         costume=(("Attendant's Formal Wear", "P"),)),
    Area(18, "Crystal Palace Interior", life=("", ""), memory=("",),
         costume=(("Gauntlets of Darkness", "P"),), strength=("P",)),
    # Zone 19
    Area(19, "Loll'ur River", life=("",), memory=("",), costume=(("Dark Costume", ""),)),
    # Zone 20
    Area(20, "Arkela Castle Courtyard", life=("", "", ""), costume=(("Guardian's Costume", ""),),
         upgrade=(("P", ""),)),
    Area(20, "Arkela Castle Hall", life=("", "")),
    # Zone 21
    Area(21, "Arkela Castle Main Tower", life=("", "")),
    Area(21, "Arkela Castle Grand Staircase", life=("P", ""), costume=(("Armor of Darkness", ""),),
         upgrade=(("P", ""),)),
]

ZONE_COUNT = max(a.zone for a in AREAS)


def zone_region_name(zone: int) -> str:
    names = " + ".join(a.name for a in AREAS if a.zone == zone)
    return f"Zone {zone:02d}: {names}"


def power_names(letters: str) -> frozenset[str]:
    return frozenset(POWERS[c] for c in letters)


class LocationData(NamedTuple):
    name: str
    zone: int
    category: str
    requirements: frozenset[str]
    missable: bool = False


def _numbered(label: str, count: int, index: int) -> str:
    return label if count == 1 else f"{label} {index}"


def _build_locations() -> list[LocationData]:
    result: list[LocationData] = []
    for area in AREAS:
        for i, req in enumerate(area.life, 1):
            result.append(LocationData(f"{area.name} - {_numbered('Life Chest', len(area.life), i)}",
                                       area.zone, "Life Chests", power_names(req), area.missable))
        for i, req in enumerate(area.memory, 1):
            result.append(LocationData(f"{area.name} - {_numbered('Memory Shard', len(area.memory), i)}",
                                       area.zone, "Memory Shards", power_names(req), area.missable))
        for i, (piece, req) in enumerate(area.costume, 1):
            label = f"Costume Chest ({piece})" if piece else _numbered("Costume Chest", len(area.costume), i)
            result.append(LocationData(f"{area.name} - {label}", area.zone, "Costume Chests",
                                       power_names(req), area.missable))
        for i, req in enumerate(area.stamina, 1):
            result.append(LocationData(f"{area.name} - {_numbered('Stamina Fruit', len(area.stamina), i)}",
                                       area.zone, "Stamina Fruits", power_names(req), area.missable))
        for i, req in enumerate(area.strength, 1):
            result.append(LocationData(f"{area.name} - {_numbered('Strength Fruit', len(area.strength), i)}",
                                       area.zone, "Strength Fruits", power_names(req), area.missable))
        for power, req in area.upgrade:
            result.append(LocationData(f"{area.name} - {POWERS[power].split()[0]} Upgrade Fruit",
                                       area.zone, "Upgrade Fruits", power_names(req), area.missable))
    for letter, (zone, area_name) in POWER_SPOTS.items():
        result.append(LocationData(f"{area_name} - {POWERS[letter]}", zone, "Powers", frozenset()))
    for boss, zone in BOSS_ZONES.items():
        result.append(LocationData(f"Boss {boss} Defeated", zone, "Bosses",
                                   power_names(BOSS_REQUIREMENTS[boss])))
    return result


LOCATIONS: list[LocationData] = _build_locations()
LOCATION_NAME_TO_ID: dict[str, int] = {loc.name: LOCATION_BASE_ID + i for i, loc in enumerate(LOCATIONS)}
assert len(LOCATION_NAME_TO_ID) == len(LOCATIONS), "duplicate location names"

LOCATION_GROUPS: dict[str, set[str]] = {}
for _loc in LOCATIONS:
    LOCATION_GROUPS.setdefault(_loc.category, set()).add(_loc.name)

# --- Items -------------------------------------------------------------------------------------------------
XP_ITEM = "Life Shards (XP)"

COSTUME_ITEMS: list[str] = [
    "Guard Knight Helm", "Guard Knight's Gauntlets", "Guard Knight Armor",
    "Bandit's Hood", "Bandit's Manifer", "Bandit's Costume",
    "Scholar's Hat", "Scholar's Cuff", "Scholar's Clothes",
    "Marine's Manifer", "Marine's Uniform", "Marine's Cap",
    "Attendant's Decorative Sleeve", "Attendant's Formal Cap", "Attendant's Formal Wear",
    "Helm of Darkness", "Gauntlets of Darkness", "Armor of Darkness",
    "Guardian's Costume", "Dark Costume",
]


def _count(field: str) -> int:
    return sum(len(getattr(a, field)) for a in AREAS)


def _upgrade_count(letter: str) -> int:
    return sum(1 for a in AREAS for power, _ in a.upgrade if power == letter)


# name -> how many copies go in the pool (powers and filler are handled separately)
FRUIT_ITEMS: dict[str, int] = {
    "Stamina Fruit": _count("stamina"),
    "Strength Fruit": _count("strength"),
    **{f"{POWERS[c].split()[0]} Upgrade Fruit": _upgrade_count(c) for c in POWERS},
}

ITEM_NAMES: list[str] = [*POWERS.values(), *FRUIT_ITEMS, *COSTUME_ITEMS, XP_ITEM]
ITEM_NAME_TO_ID: dict[str, int] = {name: ITEM_BASE_ID + i for i, name in enumerate(ITEM_NAMES)}

ITEM_GROUPS: dict[str, set[str]] = {
    "Powers": set(POWERS.values()),
    "Fruits": set(FRUIT_ITEMS),
    "Costumes": set(COSTUME_ITEMS),
}
