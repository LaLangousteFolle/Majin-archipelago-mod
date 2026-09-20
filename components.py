from worlds.LauncherComponents import Component, Type, components, launch as launch_component

from . import data


def run_client(*args: str) -> None:
    from .client.client import launch

    launch_component(launch, name="Majin Client", args=args)


components.append(
    Component(
        "Majin Client",
        func=run_client,
        game_name=data.GAME_NAME,
        component_type=Type.CLIENT,
        supports_uri=True,
    )
)
