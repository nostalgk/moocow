from evennia import AttributeProperty, DefaultObject
from evennia.utils.utils import make_iter
from evennia.utils import search
from .utils import get_obj_stats
from .enums import WieldLocation, ObjType, Ability


class EvAdventureObject(DefaultObject):
    """
    Base for all objects.

    """

    inventory_use_slot = WieldLocation.BACKPACK
    size = AttributeProperty(1, autocreate=False)
    value = AttributeProperty(0, autocreate=False)

    # this can either be a single type or a list of types (for objects able to
    # act as multiple). This is used to tag this object during creation.
    obj_type = ObjType.GEAR

    def at_object_creation(self):
        """Called when this object is first created. We convert the .obj_type
        property to a database tag."""

        for obj_type in make_iter(self.obj_type):
            self.tags.add(self.obj_type.value, category="obj_type")

    def get_help(self):
        """Get any help text for this item"""
        return "No help for this item"

    # this is in the exercise, figure it's a good idea to keep around

    # The at_object_creation is a method Evennia calls on every child of DefaultObject whenever
    # it is first created.

    # We do a tricky thing here, converting our .obj_type to one or more Tags.
    # Tagging the object like this means you can later efficiently find all objects of a given type
    # (or combination of types) with Evennia’s search functions:

    # We allow .obj_type to be given as a single value or a list of values.
    # We use make_iter from the evennia utility library to make sure we don’t balk at either.
    # This means you could have a Shield that is also Magical, for example.

    def search_shields(self):
        # get all shields in the game
        all_shields = search.search_object_by_tag(
            ObjType.SHIELD.value, category="obj_type"
        )


class EvAdventureQuestObject(EvAdventureObject):
    """Quest objects are not usually possible to sell or trade."""

    obj_type = ObjType.QUEST


class EvAdventureTreasure(EvAdventureObject):
    """Treasure is mainly used to sell for currency."""

    obj_type = ObjType.TREASURE
    value = AttributeProperty(100, autocreate=False)


class EvAdventureConsumable(EvAdventureObject):
    """An item that can be used up"""

    obj_type = ObjType.CONSUMABLE
    value = AttributeProperty(0.25, autocreate=False)
    uses = AttributeProperty(1, autocreate=False)

    def at_pre_use(self, user, *args, **kwargs):
        """Called before using. If returning False, abort use."""
        return self.uses > 0

    def at_use(self, user, *args, **kwargs):
        """Called when using the item"""
        pass

    def at_post_use(self, user, *args, **kwargs):
        """Called after using the item"""
        # detract a usage, deleting the item if used up
        self.uses -= 1

        if self.uses <= 0:
            message = f"{self.key} was used up."
            user.msg(message)
            self.delete()
            return message


class EvAdventureWeapon(EvAdventureObject):
    """Base class for all weapons"""

    obj_type = ObjType.WEAPON
    inventory_use_slot = AttributeProperty(WieldLocation.WEAPON_HAND, autocreate=False)
    quality = AttributeProperty(3, autocreate=False)

    attack_type = AttributeProperty(Ability.STR, autocreate=False)
    defend_type = AttributeProperty(Ability.ARMOR, autocreate=False)

    damage_roll = AttributeProperty("1d6", autocreate=False)


class EvAdventureRuneStone(EvAdventureWeapon, EvAdventureConsumable):
    """Base for all magical rune stones"""

    obj_type = (ObjType.WEAPON, ObjType.MAGIC)
    inventory_use_slot = WieldLocation.TW0_HANDS
    quality = AttributeProperty(3, autocreate=False)

    attack_type = AttributeProperty(Ability.INT, autocreate=False)
    defend_type = AttributeProperty(Ability.DEX, autocreate=False)

    damage_roll = AttributeProperty("1d8", autocreate=False)

    def at_post_use(self, user, *args, **kwargs):
        """Called after usage/spell was cast"""
        self.uses -= 1
        # it's not deleted, but restored after next rest

    def refresh(self):
        """Refresh the rune stone (normally after rest)"""
        self.uses = 1


class EvAdventureArmor(EvAdventureObject):
    obj_type = ObjType.ARMOR
    inventory_use_slot = WieldLocation.BODY

    armor = AttributeProperty(1, autocreate=False)
    quality = AttributeProperty(3, autocreate=False)


class EvAdventureShield(EvAdventureArmor):
    obj_type = ObjType.SHIELD
    inventory_use_slot = WieldLocation.SHIELD_HAND


class EvAdventureHelmet(EvAdventureArmor):
    obj_type = ObjType.HELMET
    inventory_use_slot = WieldLocation.HEAD


class WeaponEmptyHand(EvAdventureWeapon):
    obj_type = ObjType.WEAPON
    key = "Empty Hands"
    inventory_use_slot = WieldLocation.WEAPON_HAND
    attack_type = Ability.STR
    defense_type = Ability.ARMOR
    damage_roll = "1d4"
    quality = 100000

    def __repr__(self):
        return "<WeaponEmptyHand>"
