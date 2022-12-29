from .tables import chargen_tables
from .rules import dice
from .characters import EvAdventureCharacter
from evennia import create_object, EvMenu
from evennia.prototypes.spawner import spawn

_TEMP_SHEET = """
{name}

STR +{strength}
DEX +{dexterity}
END +{endurance}
INT +{intelligence}
WIS +{perception}
CHA +{willpower}

{description}

Your belongings:
{equipment}
"""

_ABILITIES = {
    "STR": "strength",
    "DEX": "dexterity",
    "END": "endurance",
    "INT": "intellgence",
    "PER": "perception",
    "WIL": "willpower"
}


class TemporaryCharacterSheet:
    def _random_ability(self):
        return min(dice.roll("1d6")), dice.roll("1d6"), dice.roll("1d6")

    def __init__(self):
        self.ability_changes = 0  # how many times we swapped abilities

        # name will likely be modified later
        self.name = dice.roll_random_table("1d282", dice.roll("1d6"))

        # base attributes
        self.strength = self._random_ability()
        self.dexterity = self._random_ability()
        self.endurance = self._random_ability()
        self.intelligence = self._random_ability()
        self.perception = self._random_ability()
        self.willpower = self._random_ability()

        # physical attributes (for rp purposes)
        physique = dice.roll_random_table("1d20", chargen_tables["physique"])
        face = dice.roll_random_table("1d20", chargen_tables["face"])
        skin = dice.roll_random_table("1d20", chargen_tables["skin"])
        hair = dice.roll_random_table("1d20", chargen_tables["hair"])
        clothing = dice.roll_random_table("1d20", chargen_tables["clothing"])
        speech = dice.roll_random_table("1d20", chargen_tables["speech"])
        virtue = dice.roll_random_table("1d20", chargen_tables["virtue"])
        vice = dice.roll_random_table("1d20", chargen_tables["vice"])
        background = dice.roll_random_table("1d20", chargen_tables["background"])
        misfortune = dice.roll_random_table("1d20", chargen_tables["misfortune"])
        alignment = dice.roll_random_table("1d20", chargen_tables["alignment"])

        self.desc = (
            f"You are {physique} with a {face} face, {skin} skin, {hair} hair, {speech} speech,"
            f" and {clothing} clothing. You were a {background.title()}, but you were"
            f" {misfortune} and ended up a knave. You are {virtue} but also {vice}. You are of the"
            f" {alignment} alignment."
        )

        self.hp_max = max(5, dice.roll("1d8"))
        self.hp = self.hp_max
        self.xp = 0
        self.level = 1

        # random equipment
        self.armor = dice.roll_random_table("1d20", chargen_tables["armor"])

        _helmet_and_shield = dice.roll_random_table(
            "1d20", chargen_tables["helmets and shields"]
        )
        self.helmet = "helmet" if "helmet" in _helmet_and_shield else "none"
        self.shield = "shield" if "shield" in _helmet_and_shield else "none"

        self.weapon = dice.roll_random_table("1d20", chargen_tables["starting weapon"])

        self.backpack = [
            "ration",
            "ration",
            dice.roll_random_table("1d20", chargen_tables["dungeoning gear"]),
            dice.roll_random_table("1d20", chargen_tables["dungeoning gear"]),
            dice.roll_random_table("1d20", chargen_tables["general gear 1"]),
            dice.roll_random_table("1d20", chargen_tables["general gear 2"]),
        ]

    def show_sheet(self):
        equipment = (
            str(item)
            for item in [self.armor, self.helmet, self.shield, self.weapon]
            + self.backpack
            if item
        )

        return _TEMP_SHEET.format(
            name=self.name,
            strength=self.strength,
            dexterity=self.dexterity,
            endurance=self.endurance,
            intelligence=self.intelligence,
            perception=self.perception,
            willpower=self.willpower,
            description=self.desc,
            equipment=", ".join(equipment),
        )

    def apply(self):
        # create character object with given abilities
        new_character = create_object(
            EvAdventureCharacter,
            key=self.name,
            attrs=(
                ("strength", self.strength),
                ("dexterity", self.dexterity),
                ("endurance", self.endurance),
                ("intellgence", self.intelligence),
                ("perception", self.perception),
                ("willpower", self.willpower),
                ("hp", self.hp),
                ("hp_max", self.hp_max),
                ("desc", self.desc),
            ),
        )
        # spawn equipment (requires prototypes)
        if self.weapon:
            weapon = spawn(self.weapon)
            new_character.equipment.move(weapon)
        if self.shield:
            shield = spawn(self.shield)
            new_character.equipment.move(shield)
        if self.armor:
            armor = spawn(self.armor)
            new_character.equipment.move(armor)
        if self.helmet:
            helmet = spawn(self.helmet)
            new_character.equipment.move(helmet)
            
        for item in self.backpack:
            item = spawn(item)
            new_character.equipment.store(item)
            
        return new_character
    
    def node_chargen(caller, raw_string, **kwargs):
        
        tmp_character = kwargs["tmp_character"]
        
        text = tmp_character.show_sheet()
        
        options = [
            {
                "desc" : "Change your name",
                "goto" : ("node_change_name", kwargs)
            }
        ]
        
        if tmp_character.ability_changes <= 0:
            options.append(
                {
                    "desc" : "Swap two of your ability scores (one time)",
                    "goto": ("node_swap_abilities", kwargs)
                },
            )
        options.append(
            {
                "desc" : "Accept and create character",
                "goto" : ("node_apply_character", kwargs)
            },
        )
        
        return text, options
    
    def _update_name(caller, raw_string, **kwargs):
        """
        Used by node_change_name below to check what user entered
        and updates the name if appropriate
        """
        if raw_string:
            tmp_character = kwargs["tmp_character"]
            tmp_character.name = raw_string.lower().capitalize()
            
        return "node_chargen", kwargs
    
    def node_change_name(caller, raw_string, **kwargs):
        """
        Change the random name of the character.
        """
        tmp_character = kwargs["tmp_character"]
        
        text = (
            f"Your current name is |w{tmp_character.name}|n. "
        )

    def start_chargen(caller, session=None):
        """
        This is a start point for spinning up chargen from a command later
        """
        
        menutree = {} # TODO
        
        # generate all random components of the character
        tmp_character = TemporaryCharacterSheet()
        
        EvMenu(caller, menutree, session=session, tmp_character=tmp_character)