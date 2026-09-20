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

class Boss(NamedTuple):
    name: str
    region: str  # region where the fight happens (last region before the seal that it opens)
    requirements: str  # power letters needed to win (cumulative on purpose: never softlocks)


# Names verified against the trophy list; order verified against the Karmikazzee walkthrough (GameFAQs).
BOSSES: dict[int, Boss] = {
    1: Boss("Caprakan", "Excavation Site", "W"),  # Moccoi Ruins - Great Temple, right after the Excavation Site
    2: Boss("B'alam", "Experimental Wing", "WL"),  # Great Tree Malawa - Antenna
    3: Boss("Tlaloc", "Chibirias Engine", "WLF"),  # Chibirias - Bow, after the Engine
    4: Boss("Ixtab", "Crystal Palace Interior", "WLFP"),  # Blue Crystal Cavern
}
FINAL_BOSS = Boss("Xolotl", "Arkela Castle Grand Staircase", "WLFP")  # Arkela Castle - Chapel

# Where the story hands each power to the player (area name). Confirmed by the player and the walkthrough.
POWER_SPOTS: dict[str, str] = {
    "W": "Graveyard",
    "L": "Research Wing",
    "F": "Chibirias Stern",
    "P": "Crystal Palace Courtyard",
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
    Area(7, "Kanay Valley", life=("", ""), memory=("",), strength=("",)),
    Area(7, "Wana Mu'bi Fortress", life=("", ""), memory=("",), costume=(("Scholar's Cuff", ""),),
         stamina=("",)),
    # Zone 8
    Area(8, "Royal Garden", life=("", ""), memory=("",), upgrade=(("W", ""),)),
    # Zone 9 (lightning power, boss 2)
    Area(9, "Research Wing", life=("", ""), memory=("",), strength=("",)),
    Area(9, "Experimental Wing", life=("", ""), memory=("",), costume=(("", ""),), stamina=("",)),
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

class RouteNode(NamedTuple):
    """A region of the game. parent: where you come from (None = start of the game).
    gate_boss: a boss that must be beaten to enter. entry: powers needed to enter.
    Order and connections follow the actual game (Karmikazzee walkthrough), not the collectible guide sections."""

    name: str
    parent: str | None
    gate_boss: int | None = None
    entry: str = ""
    areas: tuple[str, ...] = ()  # collectible areas inside; defaults to (name,)


ROUTE: list[RouteNode] = [
    RouteNode("Arkela Castle Start", None, areas=("Underground Storehouse", "Royal Chambers", "Corridor")),
    RouteNode("Arkela Castle Gate", "Arkela Castle Start"),
    RouteNode("Ungdo Flower Patch", "Arkela Castle Gate"),
    RouteNode("Tagalo Forest Checkpoint", "Ungdo Flower Patch"),
    RouteNode("Toto Waterfall Power Plant", "Tagalo Forest Checkpoint"),
    RouteNode("B'alam Laboratory", "Toto Waterfall Power Plant"),
    RouteNode("Potrachi Altar", "Toto Waterfall Power Plant"),
    RouteNode("Graveyard", "Potrachi Altar"),
    RouteNode("Excavation Site", "Graveyard", entry="W"),
    RouteNode("Hawme'a Falls", "Excavation Site", gate_boss=1),
    RouteNode("Denguey Forest Tower", "Hawme'a Falls"),
    RouteNode("Pele Bridge", "Denguey Forest Tower"),
    RouteNode("Tangalo'a Swamp", "Denguey Forest Tower"),
    RouteNode("Kanay Valley", "Tangalo'a Swamp"),
    RouteNode("Wana Mu'bi Fortress", "Kanay Valley"),
    RouteNode("Royal Garden", "Wana Mu'bi Fortress"),
    RouteNode("Research Wing", "Wana Mu'bi Fortress"),
    RouteNode("Experimental Wing", "Research Wing", entry="L"),
    # The room of transport opened by boss 2 leads back to Potrachi Altar, then to the cargo shed
    RouteNode("Pualata Cargo Shed", "Potrachi Altar", gate_boss=2),
    RouteNode("Dudugera Way", "Pualata Cargo Shed"),
    RouteNode("Ravine Dig Site", "Dudugera Way"),
    RouteNode("Naval Equipment Warehouse", "Ravine Dig Site"),
    RouteNode("Kingdom Navy Headquarters", "Naval Equipment Warehouse"),
    RouteNode("Iron Factory", "Kingdom Navy Headquarters"),
    RouteNode("Earth Furnace", "Iron Factory"),
    RouteNode("Chibirias Stern", "Earth Furnace"),
    RouteNode("Chibirias Engine", "Chibirias Stern", entry="F"),
    RouteNode("Koom Honu'a Passage", "Earth Furnace", gate_boss=3),
    RouteNode("Moonglow Cave", "Koom Honu'a Passage"),
    RouteNode("Koonapipi Mines", "Moonglow Cave"),
    RouteNode("Four Windmills Hill", "Koonapipi Mines"),
    RouteNode("Tanya Mafta City", "Koonapipi Mines"),
    RouteNode("Tu Kabinana Residence", "Tanya Mafta City"),
    RouteNode("Crystal Palace Courtyard", "Moonglow Cave"),
    RouteNode("Crystal Palace Interior", "Crystal Palace Courtyard", entry="P"),
    RouteNode("Loll'ur River", "Tanya Mafta City", gate_boss=4),
    RouteNode("Arkela Castle Courtyard", "Loll'ur River"),
    RouteNode("Arkela Castle Hall", "Arkela Castle Courtyard"),
    RouteNode("Arkela Castle Main Tower", "Arkela Castle Hall"),
    RouteNode("Arkela Castle Grand Staircase", "Arkela Castle Main Tower"),
]

AREA_TO_REGION: dict[str, str] = {}
for _node in ROUTE:
    for _area in (_node.areas or (_node.name,)):
        AREA_TO_REGION[_area] = _node.name
assert set(AREA_TO_REGION) == {a.name for a in AREAS}, "every area must belong to exactly one region"
assert len({n.name for n in ROUTE}) == len(ROUTE), "duplicate region names"


def power_names(letters: str) -> frozenset[str]:
    return frozenset(POWERS[c] for c in letters)


class LocationData(NamedTuple):
    name: str
    region: str
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
                                       AREA_TO_REGION[area.name], "Life Chests", power_names(req), area.missable))
        for i, req in enumerate(area.memory, 1):
            result.append(LocationData(f"{area.name} - {_numbered('Memory Shard', len(area.memory), i)}",
                                       AREA_TO_REGION[area.name], "Memory Shards", power_names(req), area.missable))
        for i, (piece, req) in enumerate(area.costume, 1):
            label = f"Costume Chest ({piece})" if piece else _numbered("Costume Chest", len(area.costume), i)
            result.append(LocationData(f"{area.name} - {label}", AREA_TO_REGION[area.name], "Costume Chests",
                                       power_names(req), area.missable))
        for i, req in enumerate(area.stamina, 1):
            result.append(LocationData(f"{area.name} - {_numbered('Stamina Fruit', len(area.stamina), i)}",
                                       AREA_TO_REGION[area.name], "Stamina Fruits", power_names(req), area.missable))
        for i, req in enumerate(area.strength, 1):
            result.append(LocationData(f"{area.name} - {_numbered('Strength Fruit', len(area.strength), i)}",
                                       AREA_TO_REGION[area.name], "Strength Fruits", power_names(req), area.missable))
        for power, req in area.upgrade:
            result.append(LocationData(f"{area.name} - {POWERS[power].split()[0]} Upgrade Fruit",
                                       AREA_TO_REGION[area.name], "Upgrade Fruits", power_names(req), area.missable))
    for letter, area_name in POWER_SPOTS.items():
        result.append(LocationData(f"{area_name} - {POWERS[letter]}", AREA_TO_REGION[area_name], "Powers",
                                   frozenset()))
    for boss in BOSSES.values():
        result.append(LocationData(f"{boss.name} Defeated", boss.region, "Bosses", power_names(boss.requirements)))
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
