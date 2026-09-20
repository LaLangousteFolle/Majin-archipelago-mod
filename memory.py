"""Memory access layer. No Archipelago imports here so it can also be used by standalone dev tools.

Xbox 360 memory is big-endian, so every integer helper reads/writes big-endian.

Backends:
  ProcMemBackend  Linux (Steam Deck / Bazzite): Xenia runs under Wine/Proton, read through /proc/<pid>/mem.
                  Needs ptrace access (same user + kernel.yama.ptrace_scope=0, or run as root).
  PymemBackend    Windows: `pip install pymem`.
  FakeBackend     In-memory fake game, used for tests and development without the emulator.
"""
from __future__ import annotations

import os
import sys
from abc import ABC, abstractmethod


class MemoryAccessError(Exception):
    """Raised when the game memory cannot be read or written (emulator closed, bad address...)."""


class MemoryBackend(ABC):
    name = "abstract"

    @abstractmethod
    def attach(self) -> bool:
        """Try to attach to the emulator process. Returns True when reads/writes can be attempted."""

    @abstractmethod
    def read(self, address: int, size: int) -> bytes: ...

    @abstractmethod
    def write(self, address: int, data: bytes) -> None: ...

    # -- helpers (big-endian) ---------------------------------------------------------------------------------
    def read_int(self, address: int, size: int = 4) -> int:
        return int.from_bytes(self.read(address, size), "big")

    def write_int(self, address: int, value: int, size: int = 4) -> None:
        value = max(0, min(value, (1 << (8 * size)) - 1))
        self.write(address, value.to_bytes(size, "big"))


class ProcMemBackend(MemoryBackend):
    name = "proc"

    def __init__(self, process_prefix: str = "xenia_canary") -> None:
        # /proc/<pid>/comm is truncated to 15 chars ("xenia_canary.ex"), so match on a prefix.
        self.process_prefix = process_prefix
        self.pid: int | None = None

    def _find_pid(self) -> int | None:
        for entry in os.listdir("/proc"):
            if not entry.isdigit():
                continue
            try:
                with open(f"/proc/{entry}/comm") as f:
                    if f.read().strip().startswith(self.process_prefix):
                        return int(entry)
            except OSError:
                continue
        return None

    def attach(self) -> bool:
        if self.pid is not None and os.path.exists(f"/proc/{self.pid}"):
            return True
        self.pid = self._find_pid()
        return self.pid is not None

    def read(self, address: int, size: int) -> bytes:
        if self.pid is None and not self.attach():
            raise MemoryAccessError("emulator process not found")
        try:
            with open(f"/proc/{self.pid}/mem", "rb", buffering=0) as f:
                f.seek(address)
                data = f.read(size)
        except (OSError, OverflowError, ValueError) as e:
            self.pid = None
            raise MemoryAccessError(f"read {address:#x} failed: {e}") from e
        if len(data) != size:
            raise MemoryAccessError(f"short read at {address:#x}")
        return data

    def write(self, address: int, data: bytes) -> None:
        if self.pid is None and not self.attach():
            raise MemoryAccessError("emulator process not found")
        try:
            with open(f"/proc/{self.pid}/mem", "r+b", buffering=0) as f:
                f.seek(address)
                f.write(data)
        except (OSError, OverflowError, ValueError) as e:
            self.pid = None
            raise MemoryAccessError(f"write {address:#x} failed: {e}") from e


class PymemBackend(MemoryBackend):
    name = "pymem"

    def __init__(self, process_name: str = "xenia_canary.exe") -> None:
        self.process_name = process_name
        self.pm = None

    def attach(self) -> bool:
        if self.pm is not None:
            return True
        try:
            import pymem  # imported lazily: Windows only
            self.pm = pymem.Pymem(self.process_name)
            return True
        except Exception:
            self.pm = None
            return False

    def read(self, address: int, size: int) -> bytes:
        if self.pm is None and not self.attach():
            raise MemoryAccessError("emulator process not found")
        try:
            return bytes(self.pm.read_bytes(address, size))
        except Exception as e:
            self.pm = None
            raise MemoryAccessError(f"read {address:#x} failed: {e}") from e

    def write(self, address: int, data: bytes) -> None:
        if self.pm is None and not self.attach():
            raise MemoryAccessError("emulator process not found")
        try:
            self.pm.write_bytes(address, data, len(data))
        except Exception as e:
            self.pm = None
            raise MemoryAccessError(f"write {address:#x} failed: {e}") from e


class FakeBackend(MemoryBackend):
    """A fake game: memory is a dict of bytes, everything unset reads as 0."""

    name = "fake"

    def __init__(self) -> None:
        self.mem: dict[int, int] = {}

    def attach(self) -> bool:
        return True

    def read(self, address: int, size: int) -> bytes:
        return bytes(self.mem.get(address + i, 0) for i in range(size))

    def write(self, address: int, data: bytes) -> None:
        for i, b in enumerate(data):
            self.mem[address + i] = b


def default_backend(kind: str | None = None) -> MemoryBackend:
    """kind: "proc", "pymem", "fake" or None to pick from the platform (env MAJIN_BACKEND overrides)."""
    kind = kind or os.environ.get("MAJIN_BACKEND") or ("pymem" if sys.platform == "win32" else "proc")
    if kind == "fake":
        return FakeBackend()
    if kind == "pymem":
        return PymemBackend()
    if kind == "proc":
        return ProcMemBackend()
    raise ValueError(f"unknown memory backend {kind!r}")
