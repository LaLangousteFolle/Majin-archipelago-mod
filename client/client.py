from __future__ import annotations

import asyncio
import json
import os
from typing import TYPE_CHECKING, Any

import colorama

from CommonClient import (
    ClientCommandProcessor,
    CommonContext,
    get_base_parser,
    handle_url_arg,
    logger,
    server_loop,
)
from NetUtils import ClientStatus
from Utils import gui_enabled, init_logging, user_path

from .. import data
from .addresses import AddressTable, fake_table, load_table
from .game import FAILED, UNSUPPORTED, MajinGame
from .memory import FakeBackend, MemoryBackend, default_backend

if TYPE_CHECKING:
    import kvui

ITEM_ID_TO_NAME = {item_id: name for name, item_id in data.ITEM_NAME_TO_ID.items()}
POLL_SECONDS = 0.5


class MajinCommandProcessor(ClientCommandProcessor):
    ctx: "MajinContext"

    def _cmd_status(self) -> None:
        """Show the emulator link and how many locations/items are handled."""
        ctx = self.ctx
        game = ctx.game_iface
        logger.info(f"Memory backend: {game.backend.name}, emulator {'found' if game.ready() else 'NOT found'}")
        logger.info(f"XP in game: {game.read_xp()}")
        logger.info(f"Addresses: {game.table.summary()}")
        logger.info(f"Items applied: {ctx.applied_index}/{len(ctx.items_received)}")

    def _cmd_reload_addresses(self) -> None:
        """Reload majin_addresses.json without restarting the client."""
        ctx = self.ctx
        table, warnings = load_table(ctx.addresses_path)
        for warning in warnings:
            logger.warning(f"addresses: {warning}")
        ctx.game_iface.table = table
        logger.info(f"Addresses reloaded: {table.summary()}")

    def _cmd_resync_items(self) -> None:
        """Forget which received items were already given, so all of them are applied again.
        Use it after starting a new save."""
        self.ctx.applied_index = 0
        self.ctx.save_applied_index()
        logger.info("Item index reset: every received item will be applied again.")

    def _cmd_fake_check(self, *location: str) -> None:
        """Development only (fake backend): mark a location as checked in the fake game."""
        game = self.ctx.game_iface
        name = " ".join(location)
        flag = game.table.location_flags.get(name)
        if not isinstance(game.backend, FakeBackend) or flag is None:
            logger.info("Only available with the fake backend and an existing location name.")
            return
        game.backend.write_int(game.table.base + flag.address, flag.mask, flag.size)
        logger.info(f"Fake check set for {name}")


class MajinContext(CommonContext):
    game = data.GAME_NAME
    items_handling = 0b111  # the server sends every item, including our own: the client gives them in game
    command_processor = MajinCommandProcessor

    def __init__(self, server_address: str | None, password: str | None, backend: MemoryBackend,
                 table: AddressTable, addresses_path: str | None = None) -> None:
        super().__init__(server_address, password)
        self.addresses_path = addresses_path
        self.game_iface = MajinGame(backend, table)
        self.slot_data: dict[str, Any] = {}
        self.shuffle_powers = False
        self.applied_index = 0
        self.finished = False
        self._was_ready: bool | None = None
        self._warned_items: set[str] = set()
        self.game_task: asyncio.Task | None = None

    # -- connection -------------------------------------------------------------------------------------------
    async def server_auth(self, password_requested: bool = False) -> None:
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect(game=self.game)

    def on_package(self, cmd: str, args: dict[str, Any]) -> None:
        if cmd == "Connected":
            self.slot_data = args.get("slot_data", {})
            self.shuffle_powers = bool(self.slot_data.get("shuffle_powers", False))
            self.applied_index = self._load_applied_index()
            self.finished = False
            logger.info(f"Connected. Powers shuffled: {self.shuffle_powers}. "
                        f"Items already given in game: {self.applied_index}")

    def make_gui(self) -> "type[kvui.GameManager]":
        from kvui import GameManager

        class MajinManager(GameManager):
            base_title = "Archipelago Majin Client"

        return MajinManager

    # -- persistence of the item index (items are not idempotent: never give them twice) -----------------------
    def _state_key(self) -> str:
        return f"{self.seed_name}:{self.team}:{self.slot}"

    def _load_applied_index(self) -> int:
        try:
            with open(user_path("majin_client_state.json")) as f:
                return int(json.load(f).get(self._state_key(), 0))
        except (OSError, ValueError):
            return 0

    def save_applied_index(self) -> None:
        path = user_path("majin_client_state.json")
        try:
            try:
                with open(path) as f:
                    state = json.load(f)
            except (OSError, ValueError):
                state = {}
            state[self._state_key()] = self.applied_index
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump(state, f)
        except OSError as e:
            logger.warning(f"Could not save the client state: {e}")

    # -- main polling step ------------------------------------------------------------------------------------
    async def tick(self) -> None:
        game = self.game_iface
        ready = game.ready()
        if ready != self._was_ready:
            logger.info("Game found, syncing." if ready else "Waiting for the emulator (Xenia) with Majin running...")
            self._was_ready = ready
        if not ready:
            return

        # Locations: everything flagged in game that the server does not know yet
        new_locations = game.read_checked_locations() & set(self.missing_locations)
        if new_locations:
            await self.check_locations(new_locations)

        # Items: give what was received since the last applied index
        while self.applied_index < len(self.items_received):
            item = self.items_received[self.applied_index]
            name = ITEM_ID_TO_NAME.get(item.item, f"unknown item {item.item}")
            result = game.apply_item(name, self.shuffle_powers)
            if result == FAILED:
                break  # retry on the next tick
            if result == UNSUPPORTED and name not in self._warned_items:
                self._warned_items.add(name)
                logger.warning(f"Received {name} but giving it in game is not implemented yet.")
            self.applied_index += 1
            self.save_applied_index()

        # Goal
        if not self.finished and game.goal_reached():
            self.finished = True
            await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])


async def game_loop(ctx: MajinContext) -> None:
    while not ctx.exit_event.is_set():
        await asyncio.sleep(POLL_SECONDS)
        if ctx.slot is None:
            continue
        try:
            await ctx.tick()
        except Exception as e:  # keep the client alive whatever happens in the game layer
            logger.exception(e)


async def main(args) -> None:
    backend = default_backend(args.backend)
    addresses_path = args.addresses or os.environ.get("MAJIN_ADDRESSES") or user_path("majin_addresses.json")
    if isinstance(backend, FakeBackend) and not args.addresses:
        table = fake_table()  # development: a synthetic memory layout covering everything
    else:
        table, warnings = load_table(addresses_path)
        for warning in warnings:
            logger.warning(f"addresses: {warning}")
    logger.info(f"Addresses: {table.summary()}")
    ctx = MajinContext(args.connect, args.password, backend, table, addresses_path)
    ctx.auth = args.name
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")
    if gui_enabled:
        try:
            import kvui  # noqa: F401
        except ImportError:
            logger.warning("Kivy is not installed: running in text mode (type commands here).")
        else:
            ctx.run_gui()
    ctx.run_cli()
    ctx.game_task = asyncio.create_task(game_loop(ctx), name="GameLoop")

    await ctx.exit_event.wait()
    ctx.server_address = None
    await ctx.shutdown()
    ctx.game_task.cancel()


def launch(*args: str) -> None:
    # Always set up logging: the Launcher does not do it for us, and with a stock root logger nothing would print.
    init_logging("MajinClient", exception_logger="Client")
    parser = get_base_parser(description="Majin and the Forsaken Kingdom client")
    parser.add_argument("--name", default=None, help="Slot name to connect as.")
    parser.add_argument("--backend", default=None, choices=["proc", "pymem", "fake"],
                        help="Memory backend (default: proc on Linux, pymem on Windows).")
    parser.add_argument("--addresses", default=None,
                        help="Path of the addresses JSON (default: majin_addresses.json in the Archipelago folder, "
                             "or the MAJIN_ADDRESSES environment variable).")
    parser.add_argument("url", nargs="?", help="Archipelago connection url")
    launch_args = handle_url_arg(parser.parse_args(args))

    colorama.just_fix_windows_console()
    asyncio.run(main(launch_args))
    colorama.deinit()


if __name__ == "__main__":
    import sys

    launch(*sys.argv[1:])
