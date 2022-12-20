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

class WieldLocation(Enum):
    
    BACKPACK = "backpack"
    WEAPON_HAND = "weapon_hand"
    SHIELD_HAND = "shield_hand"
    TW0_HANDS = "two_handed_weapons"
    BODY = "body" # armor
    HEAD = "head" # helmets

class ObjType(Enum):
    
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    HELMET = "helmet"
    CONSUMABLE = "consumable"
    GEAR = "gear"
    MAGIC = "magic"
    QUEST = "quest"
    TREASURE = "treasure"