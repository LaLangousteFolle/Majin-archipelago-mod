"""Game-side logic, independent from Archipelago networking (so it can be tested with a fake backend)."""
from __future__ import annotations

from .. import data
from .addresses import AddressTable, Flag
from .memory import MemoryAccessError, MemoryBackend

APPLIED = "applied"
SKIPPED = "skipped"  # nothing to do (e.g. a power the story already grants)
UNSUPPORTED = "unsupported"  # we do not know yet how to give this item in game
FAILED = "failed"  # memory access failed, try again later


class MajinGame:
    def __init__(self, backend: MemoryBackend, table: AddressTable) -> None:
        self.backend = backend
        self.table = table

    # -- state ------------------------------------------------------------------------------------------------
    def ready(self) -> bool:
        """True when the emulator is attached and the game memory looks sane."""
        if not self.backend.attach():
            return False
        if self.table.xp is None:
            return True
        try:
            xp = self.backend.read_int(self.table.base + self.table.xp, 4)
        except MemoryAccessError:
            return False
        return 0 <= xp < 10_000_000

    def read_xp(self) -> int | None:
        if self.table.xp is None:
            return None
        try:
            return self.backend.read_int(self.table.base + self.table.xp, 4)
        except MemoryAccessError:
            return None

    def _flag_set(self, flag: Flag) -> bool:
        value = self.backend.read_int(self.table.base + flag.address, flag.size)
        return bool(value & flag.mask) != flag.invert

    # -- locations --------------------------------------------------------------------------------------------
    def read_checked_locations(self) -> set[int]:
        """Archipelago location ids of every location whose flag is currently set in game."""
        checked: set[int] = set()
        for name, flag in self.table.location_flags.items():
            try:
                if self._flag_set(flag):
                    checked.add(data.LOCATION_NAME_TO_ID[name])
            except MemoryAccessError:
                break  # emulator went away, the next tick will notice
        return checked

    def goal_reached(self) -> bool:
        if self.table.goal_flag is None:
            return False
        try:
            return self._flag_set(self.table.goal_flag)
        except MemoryAccessError:
            return False

    # -- items ------------------------------------------------------------------------------------------------
    def apply_item(self, name: str, shuffle_powers: bool) -> str:
        if name in data.POWERS.values() and not shuffle_powers:
            return SKIPPED  # the story grants the powers itself
        effect = self.table.item_effects.get(name)
        if effect is None:
            return UNSUPPORTED
        address = self.table.base + effect.address
        try:
            if effect.kind == "add":
                self.backend.write_int(address, self.backend.read_int(address, effect.size) + effect.amount,
                                       effect.size)
            elif effect.kind == "set":
                self.backend.write_int(address, effect.amount, effect.size)
            elif effect.kind == "or":
                self.backend.write_int(address, self.backend.read_int(address, effect.size) | effect.amount,
                                       effect.size)
            else:
                return UNSUPPORTED
        except MemoryAccessError:
            return FAILED
        return APPLIED
