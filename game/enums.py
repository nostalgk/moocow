from enum import Enum

class Ability(Enum):
    """
    The six base ability-bonuses and other
    abilities

    """

    STR = "strength"
    DEX = "dexterity"
    END = "endurance"
    INT = "intelligence"
    PER = "perception"
    WIL = "willpower"

    ARMOR = "armor"
    WEAPON = "weapon"

    CRITICAL_FAILURE = "critical_failure"
    CRITICAL_SUCCESS = "critical_success"

    ALLEGIANCE_HOSTILE = "hostile"
    ALLEGIANCE_NEUTRAL = "neutral"
    ALLEGIANCE_FRIENDLY = "friendly"
