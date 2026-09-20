from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from BaseClasses import Item, ItemClassification, Location, LocationProgressType, Region, Tutorial
from worlds.AutoWorld import WebWorld, World

from . import data
from .options import MajinOptions, option_groups


class MajinItem(Item):
    game = data.GAME_NAME


class MajinLocation(Location):
    game = data.GAME_NAME


class MajinWebWorld(WebWorld):
    game = data.GAME_NAME
    theme = "jungle"
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Majin and the Forsaken Kingdom for Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Nono"],
    )
    tutorials = [setup_en]
    option_groups = option_groups


def _classification(name: str) -> ItemClassification:
    if name in data.POWERS.values():
        return ItemClassification.progression
    if name in data.FRUIT_ITEMS:
        return ItemClassification.useful
    return ItemClassification.filler


class MajinWorld(World):
    """
    Majin and the Forsaken Kingdom is a 2010 action-adventure game where a young thief and a giant creature,
    the Majin, explore a fallen kingdom, solving puzzles with the four elemental powers.
    """

    game = data.GAME_NAME
    web = MajinWebWorld()

    options_dataclass = MajinOptions
    options: MajinOptions

    location_name_to_id = data.LOCATION_NAME_TO_ID
    item_name_to_id = data.ITEM_NAME_TO_ID
    item_name_groups = data.ITEM_GROUPS
    location_name_groups = data.LOCATION_GROUPS

    # ---- helpers ------------------------------------------------------------------------------------------
    def _rule(self, powers: frozenset[str]):
        player = self.player
        if not powers:
            return None
        return lambda state: state.has_all(powers, player)

    # ---- generation steps ---------------------------------------------------------------------------------
    def _entry_rule(self, node: data.RouteNode):
        player = self.player
        powers = data.power_names(node.entry)
        gate = f"Boss {node.gate_boss} Beaten" if node.gate_boss else None
        if not powers and gate is None:
            return None
        return lambda state: state.has_all(powers, player) and (gate is None or state.has(gate, player))

    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)
        regions = {node.name: Region(node.name, self.player, self.multiworld) for node in data.ROUTE}
        self.multiworld.regions += [menu, *regions.values()]

        for node in data.ROUTE:
            parent = menu if node.parent is None else regions[node.parent]
            parent.connect(regions[node.name], f"{parent.name} to {node.name}", self._entry_rule(node))

        # Regular locations
        for loc in data.LOCATIONS:
            region = regions[loc.region]
            location = MajinLocation(self.player, loc.name, data.LOCATION_NAME_TO_ID[loc.name], region)
            rule = self._rule(loc.requirements)
            if rule is not None:
                location.access_rule = rule
            if loc.missable:
                # These chests are lost for good when leaving the first castle areas: never put progression there.
                location.progress_type = LocationProgressType.EXCLUDED
            region.locations.append(location)

        # Story power grants: locked in place unless the powers are shuffled
        if not self.options.shuffle_powers:
            for letter, area_name in data.POWER_SPOTS.items():
                spot = self.get_location(f"{area_name} - {data.POWERS[letter]}")
                spot.place_locked_item(self.create_item(data.POWERS[letter]))

        # Boss events (logic) and final boss (goal)
        for number, boss in data.BOSSES.items():
            regions[boss.region].add_event(
                f"Boss {number} Event", f"Boss {number} Beaten",
                rule=self._rule(data.power_names(boss.requirements)),
                location_type=MajinLocation, item_type=MajinItem,
            )
        regions[data.FINAL_BOSS.region].add_event(
            f"{data.FINAL_BOSS.name} Event", "Victory",
            rule=self._rule(data.power_names(data.FINAL_BOSS.requirements)),
            location_type=MajinLocation, item_type=MajinItem,
        )

    def set_rules(self) -> None:
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)

    def create_item(self, name: str) -> MajinItem:
        return MajinItem(name, _classification(name), data.ITEM_NAME_TO_ID[name], self.player)

    def create_items(self) -> None:
        pool: list[Item] = []
        if self.options.shuffle_powers:
            pool += [self.create_item(name) for name in data.POWERS.values()]
        for name, count in data.FRUIT_ITEMS.items():
            pool += [self.create_item(name) for _ in range(count)]
        pool += [self.create_item(name) for name in data.COSTUME_ITEMS]

        unfilled = len(self.multiworld.get_unfilled_locations(self.player))
        pool += [self.create_filler() for _ in range(unfilled - len(pool))]
        self.multiworld.itempool += pool

    def get_filler_item_name(self) -> str:
        return data.XP_ITEM

    def fill_slot_data(self) -> Mapping[str, Any]:
        return {
            "shuffle_powers": bool(self.options.shuffle_powers),
            "world_version": "0.4.0",
        }
