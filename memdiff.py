#!/usr/bin/env python3
"""memdiff: find game memory addresses and write them into majin_addresses.json, no code editing needed.

Run it from the Archipelago folder (so it finds worlds/majin/data.py and writes majin_addresses.json there),
with Xenia + the game running, and memory.py next to this file:

    python memdiff.py                     # scans +-256 KB around the XP address
    python memdiff.py --span 0x200000     # wider

Typical loop for a chest:
    b                  BEFORE snapshot (stand still in front of the chest)
    (open the chest, close every menu / reward screen, stand still)
    a                  AFTER snapshot -> numbered list of changes
    save 3 graveyard life chest 1      store change #3 as the flag of that location (names are fuzzy-matched)

A chest flag looks like 0 -> 1 on a bit, at an address that differs for each chest but sits close to the others.
For a counter (fruits...): eat/grab one, take BEFORE/AFTER, then `item 2 stamina fruit` (adds the observed step).
For the end of the game: `goal 1` after beating the final boss.

Commands:
    b | a                  BEFORE / AFTER snapshot (a prints the changes)
    save <n> <location>    change n -> location flag         (bit=K to pick another bit)
    item <n> <item>        change n -> counter added when the item is received  (amount=N to override)
    goal <n>               change n -> "final boss beaten" flag
    all                    toggle showing big values too (floats, pointers)
    noise                  recalibrate the noise filter (5 s, touch nothing)
    missing [words]        locations that still have no address
    progress               how much is mapped
    q                      quit
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time

from memory import MemoryAccessError, default_backend

XP_ADDRESS = 0x2BCA16D40
PAGE = 0x1000
DATA_CANDIDATES = ["worlds/majin/data.py", "majin/data.py", "data.py"]


# --- pure helpers (also used by the tests) ---------------------------------------------------------------------
def load_data(path: str | None = None):
    for candidate in ([path] if path else DATA_CANDIDATES):
        if candidate and os.path.exists(candidate):
            spec = importlib.util.spec_from_file_location("majin_data", candidate)
            module = importlib.util.module_from_spec(spec)
            sys.modules["majin_data"] = module
            spec.loader.exec_module(module)
            return module
    return None


def snapshot(backend, start: int, size: int) -> dict[int, bytes]:
    pages: dict[int, bytes] = {}
    for off in range(0, size, PAGE):
        try:
            pages[off] = backend.read(start + off, PAGE)
        except MemoryAccessError:
            pass  # unmapped page
    return pages


def diff(start: int, a: dict[int, bytes], b: dict[int, bytes]) -> list[tuple[int, int, int]]:
    changes = []
    for off, pa in a.items():
        pb = b.get(off)
        if not pb or pa == pb:
            continue
        for i in range(0, min(len(pa), len(pb)), 4):
            if pa[i:i + 4] != pb[i:i + 4]:
                changes.append((start + off + i, int.from_bytes(pa[i:i + 4], "big"),
                                int.from_bytes(pb[i:i + 4], "big")))
    return changes


def changed_bits(old: int, new: int) -> list[int]:
    return [i for i in range(32) if (old ^ new) >> i & 1]


def flag_from_change(address: int, old: int, new: int, bit: int | None = None) -> dict:
    """Turn a 32-bit big-endian change into a 1-byte flag entry (address of the byte holding the bit)."""
    bits = changed_bits(old, new)
    if not bits:
        raise ValueError("nothing changed")
    if bit is None:
        bit = bits[0]
    elif bit not in bits:
        raise ValueError(f"bit {bit} did not change (changed bits: {bits})")
    entry = {"address": f"0x{address + 3 - bit // 8:X}", "mask": f"0x{1 << (bit % 8):02X}"}
    if not (new >> bit) & 1:  # the bit went 1 -> 0: the location counts as checked when it is CLEAR
        entry["invert"] = True
    return entry


def resolve(query: str, names: list[str]) -> tuple[str | None, list[str]]:
    """Exact (case-insensitive) match, else every name containing all the words. Returns (name, candidates)."""
    q = query.strip().lower()
    for name in names:
        if name.lower() == q:
            return name, []
    words = q.replace("-", " ").split()
    matches = [n for n in names if all(w in n.lower().replace("-", " ") for w in words)]
    return (matches[0], []) if len(matches) == 1 else (None, matches)


def update_json(path: str, section: str | None, key: str | None, value) -> None:
    doc: dict = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
    if section is None:
        doc[key] = value
    else:
        doc.setdefault(section, {})[key] = value
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def read_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


# --- interactive session -----------------------------------------------------------------------------------
class Session:
    def __init__(self, args) -> None:
        self.backend = default_backend(args.backend)
        if not self.backend.attach():
            raise SystemExit("Emulator not found. Start Xenia with the game first.")
        self.start = args.address - args.span
        self.size = args.span * 2
        self.path = args.file
        self.limit = args.limit
        self.show_all = args.all
        self.data = load_data(args.data)
        if self.data is None:
            print("(worlds/majin/data.py not found: names will not be checked or completed. "
                  "Run from the Archipelago folder or pass --data.)")
        self.noise: set[int] = set()
        self.before: dict[int, bytes] | None = None
        self.changes: list[tuple[int, int, int]] = []

    def calibrate(self) -> None:
        print("Noise calibration: do not touch anything for 5 seconds...")
        a = snapshot(self.backend, self.start, self.size)
        time.sleep(5)
        b = snapshot(self.backend, self.start, self.size)
        self.noise = {c[0] for c in diff(self.start, a, b)}
        print(f"{len(self.noise)} noisy addresses will be ignored.")

    def take_before(self) -> None:
        self.before = snapshot(self.backend, self.start, self.size)
        print("BEFORE snapshot taken. Do the action, close menus, stand still, then type `a`.")

    def take_after(self) -> None:
        if self.before is None:
            print("Take a BEFORE snapshot first (`b`).")
            return
        after = snapshot(self.backend, self.start, self.size)
        changes = [c for c in diff(self.start, self.before, after) if c[0] not in self.noise]
        if not self.show_all:
            changes = [c for c in changes if c[1] < 0x10000 and c[2] < 0x10000]
        self.changes = changes[:self.limit]
        print(f"{len(changes)} changes" + ("" if self.show_all else " (small values only)")
              + (f", showing the first {self.limit}" if len(changes) > self.limit else "") + ":")
        for n, (addr, old, new) in enumerate(self.changes, 1):
            bits = changed_bits(old, new)
            hint = f"  bit {bits[0]}" if len(bits) == 1 else ""
            print(f"  {n:>3}  {addr:#x}  {old} -> {new}   (XP {addr - XP_ADDRESS:+#x}){hint}")
        self.before = None

    def _pick(self, token: str):
        try:
            n = int(token)
            if n < 1:
                raise IndexError
            return self.changes[n - 1]
        except (ValueError, IndexError):
            print(f"No change #{token}. Type `a` to list the changes.")
            return None

    @staticmethod
    def _options(text: str) -> tuple[str, dict[str, int]]:
        words, options = [], {}
        for word in text.split():
            if "=" in word and word.split("=")[0] in ("bit", "amount"):
                key, value = word.split("=", 1)
                options[key] = int(value, 0)
            else:
                words.append(word)
        return " ".join(words), options

    def _name(self, query: str, names: list[str], what: str) -> str | None:
        if not names:
            return query
        name, candidates = resolve(query, names)
        if name:
            return name
        if candidates:
            print(f"Several {what} match, be more precise:")
            for c in candidates[:12]:
                print("   ", c)
            if len(candidates) > 12:
                print(f"    ... and {len(candidates) - 12} more")
        else:
            print(f"No {what} matches {query!r}.")
        return None

    def cmd_save(self, rest: str) -> None:
        parts = rest.split(maxsplit=1)
        if len(parts) < 2:
            print("Usage: save <n> <location name>")
            return
        change = self._pick(parts[0])
        query, options = self._options(parts[1])
        if change is None:
            return
        names = list(self.data.LOCATION_NAME_TO_ID) if self.data else []
        name = self._name(query, names, "locations")
        if name is None:
            return
        try:
            entry = flag_from_change(*change, bit=options.get("bit"))
        except ValueError as e:
            print(e)
            return
        bits = changed_bits(change[1], change[2])
        if len(bits) > 1 and "bit" not in options:
            print(f"Careful: {len(bits)} bits changed {bits}; used bit {bits[0]}. "
                  f"Not a clean flag? Retry with bit=K, or it may be a counter.")
        update_json(self.path, "location_flags", name, entry)
        print(f"Saved  {name}: {entry}")
        self.cmd_progress()

    def cmd_item(self, rest: str) -> None:
        parts = rest.split(maxsplit=1)
        if len(parts) < 2:
            print("Usage: item <n> <item name>")
            return
        change = self._pick(parts[0])
        query, options = self._options(parts[1])
        if change is None:
            return
        names = list(self.data.ITEM_NAME_TO_ID) if self.data else []
        name = self._name(query, names, "items")
        if name is None:
            return
        address, old, new = change
        amount = options.get("amount", new - old)
        if amount <= 0:
            print(f"The value went {old} -> {new}: not a counter going up. Use amount=N to force a step.")
            return
        entry = {"kind": "add", "address": f"0x{address:X}", "size": 4, "amount": amount}
        update_json(self.path, "item_effects", name, entry)
        print(f"Saved  {name}: {entry}")

    def cmd_goal(self, rest: str) -> None:
        change = self._pick(rest.strip().split()[0]) if rest.strip() else None
        if change is None:
            return
        try:
            entry = flag_from_change(*change)
        except ValueError as e:
            print(e)
            return
        update_json(self.path, None, "goal_flag", entry)
        print(f"Saved goal_flag: {entry}")

    def cmd_progress(self) -> None:
        doc = read_json(self.path)
        flags = doc.get("location_flags", {})
        total = len(self.data.LOCATIONS) if self.data else "?"
        print(f"Mapped: {len(flags)}/{total} locations, {len(doc.get('item_effects', {}))} item effects, "
              f"goal {'yes' if 'goal_flag' in doc else 'NO'}  ({self.path})")

    def cmd_missing(self, rest: str) -> None:
        if not self.data:
            print("Needs worlds/majin/data.py.")
            return
        done = set(read_json(self.path).get("location_flags", {}))
        words = rest.lower().split()
        todo = [loc.name for loc in self.data.LOCATIONS
                if loc.name not in done and all(w in loc.name.lower() for w in words)]
        print(f"{len(todo)} locations without an address" + (f" matching {rest!r}" if rest else "") + ":")
        for name in todo[:60]:
            print("   ", name)
        if len(todo) > 60:
            print(f"    ... and {len(todo) - 60} more (add words to filter)")

    def run(self) -> None:
        self.cmd_progress()
        while True:
            try:
                line = input("memdiff> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            if not line:
                continue
            cmd, _, rest = line.partition(" ")
            cmd = cmd.lower()
            try:
                if cmd in ("q", "quit", "exit"):
                    return
                elif cmd in ("b", "before"):
                    self.take_before()
                elif cmd in ("a", "after"):
                    self.take_after()
                elif cmd == "save":
                    self.cmd_save(rest)
                elif cmd == "item":
                    self.cmd_item(rest)
                elif cmd == "goal":
                    self.cmd_goal(rest)
                elif cmd == "all":
                    self.show_all = not self.show_all
                    print("showing big values too" if self.show_all else "small values only")
                elif cmd == "noise":
                    self.calibrate()
                elif cmd == "missing":
                    self.cmd_missing(rest)
                elif cmd == "progress":
                    self.cmd_progress()
                else:
                    print("Unknown command. b, a, save, item, goal, all, noise, missing, progress, q")
            except MemoryAccessError as e:
                print(f"Memory error: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Find game memory addresses and save them to a JSON file.")
    parser.add_argument("--address", type=lambda x: int(x, 0), default=XP_ADDRESS, help="center of the scan")
    parser.add_argument("--span", type=lambda x: int(x, 0), default=0x40000, help="bytes scanned on each side")
    parser.add_argument("--backend", choices=["proc", "pymem", "fake"], default=None)
    parser.add_argument("--file", default="majin_addresses.json", help="addresses JSON to read/write")
    parser.add_argument("--data", default=None, help="path of worlds/majin/data.py (auto-detected)")
    parser.add_argument("--all", action="store_true", help="also show big values (floats, pointers)")
    parser.add_argument("--limit", type=int, default=80, help="max changes listed")
    parser.add_argument("--no-noise", action="store_true", help="skip the 5 s noise calibration")
    args = parser.parse_args()

    session = Session(args)
    if not args.no_noise:
        session.calibrate()
    session.run()


if __name__ == "__main__":
    main()
