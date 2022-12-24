from evennia.utils import create
from evennia.utils.test_resources import BaseEvenniaTest

from .. import objects
from ..characters import EvAdventureCharacter, LivingMixin
from ..enums import WieldLocation
from .. import equipment


class TestEquipment(LivingMixin,BaseEvenniaTest):
    def setUp(self):
        super().setUp()
        self.character = create.create_object(EvAdventureCharacter, key="testchar")
        self.helmet = create.create_object(objects.EvAdventureHelmet, key="helmet")
        self.weapon = create.create_object(objects.EvAdventureWeapon, key="weapon")


    def test_add_drop_remove(self):
        # add item to backpack
        self.character.equipment.add(self.helmet)
        self.assertEqual(
            self.character.equipment.slots[WieldLocation.BACKPACK],
            [self.helmet]
        )

        # remove item from backpack
        self.character.equipment.drop(self.helmet)
        self.assertEqual(self.character.equipment.slots[WieldLocation.BACKPACK], [])

    def test_remove_remove_all(self):
        # add two items to the backpack and remove them all

        self.character.equipment.add(self.helmet)
        self.character.equipment.add(self.weapon)
        self.character.equipment.remove(WieldLocation.BACKPACK)
        self.assertEqual(self.character.equipment.slots[WieldLocation.BACKPACK], [])

        self.character.equipment.slots[WieldLocation.WEAPON_HAND] = self.weapon
        self.character.equipment.remove(WieldLocation.WEAPON_HAND)
        self.assertEqual(self.character.equipment.slots[WieldLocation.WEAPON_HAND], None)
