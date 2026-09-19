from dataclasses import dataclass

from Options import OptionGroup, PerGameCommonOptions, Toggle


class ShufflePowers(Toggle):
    """
    Adds the four powers (Wind, Lightning, Fire, Purification) to the item pool.
    When off, each power stays at the place where the story gives it to you.
    The client has to block the story power grants when this is on.
    """

    display_name = "Shuffle Powers"


@dataclass
class MajinOptions(PerGameCommonOptions):
    shuffle_powers: ShufflePowers


option_groups = [
    OptionGroup("Randomization", [ShufflePowers]),
]
