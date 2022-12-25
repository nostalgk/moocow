from evennia.utils import create
from evennia.utils.test_resources import BaseEvenniaTest

from .. import objects
from ..characters import EvAdventureCharacter, LivingMixin
from ..enums import WieldLocation
from .. import equipment


class TestEquipment(LivingMixin, BaseEvenniaTest):
    def setUp(self):
        super().setUp()
        self.character = create.create_object(EvAdventureCharacter, key="testchar")
        self.helmet = create.create_object(objects.EvAdventureHelmet, key="helmet")
        self.weapon = create.create_object(objects.EvAdventureWeapon, key="sord")
        self.shield = create.create_object(objects.EvAdventureShield, key="sheeld")

    def test_add_drop_remove(self):
        # add item to backpack
        self.character.equipment.add(self.helmet)
        self.assertEqual(
            self.character.equipment.slots[WieldLocation.BACKPACK], [self.helmet]
        )
        # remove item from backpack
        self.character.equipment.drop(self.helmet)
        self.assertEqual(self.character.equipment.slots[WieldLocation.BACKPACK], [])

    def test_remove_remove_all(self):
        # add two items to the backpack and remove them all

        self.character.equipment.add(self.helmet)
        self.character.equipment.add(self.weapon)
        self.character.equipment.remove_all(WieldLocation.BACKPACK)
        self.assertEqual(self.character.equipment.slots[WieldLocation.BACKPACK], [])

        # remove a single item from the backpack
        self.character.equipment.slots[WieldLocation.WEAPON_HAND] = self.weapon
        self.character.equipment.remove(WieldLocation.WEAPON_HAND)
        self.assertEqual(
            self.character.equipment.slots[WieldLocation.WEAPON_HAND], None
        )

    def test_max_slots(self):
        # default, no endurance specified for our character
        self.assertEqual(self.character.equipment.max_slots, 11)

        self.character.endurance = 3

        # with 3 end added
        self.assertEqual(self.character.equipment.max_slots, 13)

    def test_count_slots(self):
        # testing counting used slots
        # with no items
        self.assertEqual(self.character.equipment.count_slots(), 0)

        # with an item added (uses attr "size" that is not specified)
        self.character.equipment.add(self.helmet)
        self.assertEqual(self.character.equipment.count_slots(), 1)

    def test_validate_slot_usage(self):
        # test that items are correctly evaluated in regard to their slot usage
        self.assertTrue(self.character.equipment.validate_slot_usage(self.helmet))

        # fill slots
        for _ in range(11):
            self.character.equipment.add(self.helmet)
        # see if it stops us from adding another item
        with self.assertRaises(equipment.EquipmentError) as err:
            self.character.equipment.add(self.helmet)
            str(err.exception).startswith("Equipment full")

    def test_display_slots(self):
        # tests 0 slots used by default
        result = self.character.equipment.display_slot_usage()
        self.assertTrue(result.startswith("|b0/"))

        # test that a helmet size 1 will occupy a slot
        self.character.equipment.add(self.helmet)
        result = self.character.equipment.display_slot_usage()
        self.assertTrue(result.startswith("|b1/"))

        # test that increased max slots displays correctly
        self.character.endurance = 3
        result = self.character.equipment.display_slot_usage()
        self.assertTrue(result.endswith("/13|n"))

    def test_move_equip(self):
        # tests that objects are moved to correct slots
        self.character.equipment.add(self.helmet)
        self.character.equipment.move(self.helmet)
        self.assertTrue(self.character.equipment.slots[WieldLocation.HEAD], "helmet")

        # tests that an object replaces the other object
        helm2 = create.create_object(objects.EvAdventureHelmet, key="coolerhelmet")
        self.character.equipment.add(helm2)
        self.character.equipment.move(helm2)
        self.assertTrue(
            self.character.equipment.slots[WieldLocation.HEAD], "coolerhelmet"
        )
        self.assertIn(
            self.helmet, self.character.equipment.slots[WieldLocation.BACKPACK]
        )

    def test_move_weapons(self):
        # testing that weapons correctly remove their counterparts
        # equip weapon
        self.character.equipment.add(self.weapon)
        self.character.equipment.move(self.weapon)
        self.assertTrue(
            self.character.equipment.slots[WieldLocation.WEAPON_HAND], self.weapon
        )
        # equip shield
        self.character.equipment.add(self.shield)
        self.character.equipment.move(self.shield)
        self.assertTrue(
            self.character.equipment.slots[WieldLocation.SHIELD_HAND], self.shield
        )

        # equip two-handed weapon, forcing stowage of sord and sheeld
        dragonslayer = create.create_object(
            objects.EvAdventureWeapon, key="dragonslayer"
        )
        dragonslayer.inventory_use_slot = WieldLocation.TWO_HANDS
        self.character.equipment.add(dragonslayer)
        self.character.equipment.move(dragonslayer)
        self.assertTrue(
            self.character.equipment.slots[WieldLocation.TWO_HANDS], dragonslayer
        )
        # make sure both items are now in the backpack
        self.assertTrue(
            all(
                x in self.character.equipment.slots[WieldLocation.BACKPACK]
                for x in [self.weapon, self.shield]
            )
        )
        # two handed weapon removed when equipping 1h
        self.character.equipment.move(self.weapon)
        self.assertFalse(self.character.equipment.slots[WieldLocation.TWO_HANDS])

    def test_all(self):
        # test getting all items in inventory
        self.character.equipment.add(self.helmet)
        self.character.equipment.move(self.helmet)
        self.character.equipment.add(self.weapon)
        self.character.equipment.add(self.shield)
        result = self.character.equipment.all()
        # make sure the head slot was included in the inventory with the right item
        self.assertIn((self.helmet, WieldLocation.HEAD), result)
        # something fun i wanted to add
        # returns all items in a neat list that are in the backpack
        self.assertTrue([item[0] for item in result if WieldLocation.BACKPACK in item], [self.weapon, self.shield])

    def test_inventory_function(self):
        # tests what returns from calling the inventory function
        # test empty inventory
        empty = self.character.equipment.inventory()
        self.assertTrue(empty, "Yon backpack be empty.")

        # test adding a couple items, with different sizes
        self.helmet.size = 2
        self.character.equipment.add(self.helmet)
        self.character.equipment.add(self.weapon)
        inv = self.character.equipment.inventory()
        self.assertIn("helmet : 2 slots", inv)
        self.assertIn("sord : 1 slots", inv)

    def test_identify_slot(self):
        # tests identifying slot item is in
        self.character.equipment.add(self.helmet)
        self.character.equipment.move(self.helmet)
        self.assertTrue(self.character.equipment.identify_slot(self.helmet), WieldLocation.HEAD)

    def test_identify_loadout(self):
        # tests returning equipped items
        # tests no equipment
        res = self.character.equipment.identify_loadout()
        self.assertTrue(res.startswith("You're not wearing anything"))

        # tests one equipped item
        self.character.equipment.add(self.helmet)
        self.character.equipment.move(self.helmet)
        ult = self.character.equipment.identify_loadout()
        self.assertTrue(ult, "WieldLocation.HEAD : helmet")

        # tests equipping multiple items and returning them all
        self.character.equipment.add(self.weapon)
        self.character.equipment.move(self.weapon)
        result = self.character.equipment.identify_loadout()
        self.assertTrue(result, """weapon hand : sord
        head : helmet""")

    def test_get_wearable_objects(self):
        self.character.equipment.add(self.helmet)
        self.character.equipment.add(self.helmet)
        res = self.character.equipment.get_wearable_objects_from_backpack()
        self.assertTrue(res, [self.helmet, self.helmet])

    def test_get_wieldable_objects(self):
        self.character.equipment.add(self.weapon)
        self.character.equipment.add(self.shield)
        res = self.character.equipment.get_wieldable_objects_from_backpack()
        self.assertTrue(res, [self.weapon, self.shield])

