from .enums import WieldLocation, Ability
from .objects import EvAdventureObject, WeaponEmptyHand
from evennia import utils


class EquipmentError(TypeError):
    """All types of equipment-errors"""

    pass


class EquipmentHandler:

    # we're going to need to

    save_attribute = "inventory_slots"

    def __init__(self, obj):
        # here, obj is the character we store the handler on

        self.obj = obj
        self.__load()

    def __load(self):
        """Load our data from an Attribute on `self.obj`"""
        self.slots = self.obj.attributes.get(
            self.save_attribute,
            category="inventory",
            default={
                WieldLocation.WEAPON_HAND: None,
                WieldLocation.SHIELD_HAND: None,
                WieldLocation.TWO_HANDS: None,
                WieldLocation.BODY: None,
                WieldLocation.HEAD: None,
                WieldLocation.BACKPACK: [],
            },
        )

    def _save(self):
        """Save our data back to the same attribute"""
        self.obj.attributes.add(self.save_attribute, self.slots, category="inventory")

    @property
    def max_slots(self):
        """Max amount of slots, based on END defense (END + 10)"""
        return getattr(self.obj, Ability.END.value, 1) + 10

    def count_slots(self):
        """Count current slot usage"""
        slots = self.slots
        # get the size for each object if it's not in the backpack
        wield_item_sizes = []
        for slot, slotobj in slots.items():
            if slot is not WieldLocation.BACKPACK:
                size = getattr(slotobj, "size", 0)
                wield_item_sizes.append(size)
        wield_usage = sum(wield_item_sizes)
        # get the size for each object in the backpack
        backpack_usage = sum(
            getattr(slotobj, "size", 0) for slotobj in slots[WieldLocation.BACKPACK]
        )
        return wield_usage + backpack_usage

    def validate_slot_usage(self, obj):
        """
        Check if obj can fit in equipment, based on its size.

        Args:
            obj (EvAdventureObject): The object to add.

        Raise:
            EquipmentError: If there's not enough room.

        """
        if not utils.inherits_from(obj, EvAdventureObject):
            raise EquipmentError(f"{obj.key} is not something that can be equipped.")

        size = obj.size
        max_slots = self.max_slots
        current_slot_usage = self.count_slots()
        if current_slot_usage + size > max_slots:
            slots_left = max_slots - current_slot_usage
            raise EquipmentError(
                f"Equipment full ($int2str({slots_left}) slots "
                f"remaining, {obj.key} needs $int2str({size}) "
                f"$pluralize(slot, {size}))."
            )
        return True

    def display_slot_usage(self):
        """
        Get a slot usage/max string for display.

        Returns:
            str: The usage string.

        """
        return f"|b{self.count_slots()}/{self.max_slots}|n"

    def add(self, obj):
        """Put something in the backpack."""
        self.validate_slot_usage(obj)
        self.slots[WieldLocation.BACKPACK].append(obj)
        self._save()

    def drop(self, obj):
        # Remove something from the backpack
        self.slots[WieldLocation.BACKPACK].remove(obj)
        self._save()

    def remove(self, slot):
        """Remove contents of a particular slot, for
        example `equipment.remove(WieldLocation.SHIELD_HAND)"""
        slots = self.slots
        ret = []
        ret.append(slots[slot])
        slots[slot] = None
        if ret:
            self._save()
        else:
            raise EquipmentError(f"There's nothing equipped in that slot.")

        return ret

    def remove_all(self, slot):
        """Remove all contents of a slot (dump backpack for example)"""
        slots = self.slots
        ret = []
        ret.extend(slots[slot])
        slots[slot] = []

        if ret:
            self._save()
        else:
            raise EquipmentError(f"You shake the container, and some dust floats out.")

        return ret

    def move(self, obj):
        """Move object from backpack to its intended inventory_use_slot"""

        # make sure to remove from equipment/backpack first, to avoid double-adding
        self.drop(obj)

        slots = self.slots
        use_slot = getattr(obj, "inventory_use_slot", WieldLocation.BACKPACK)

        to_backpack = []
        try:
            if use_slot is WieldLocation.TWO_HANDS:
                # TWO handed weapons can't be used with weapon/shield_hand objects
                to_backpack = [
                    slots[WieldLocation.WEAPON_HAND],
                    slots[WieldLocation.SHIELD_HAND],
                ]
                slots[WieldLocation.WEAPON_HAND] = slots[
                    WieldLocation.SHIELD_HAND
                ] = None
                slots[use_slot] = obj

            elif use_slot in (WieldLocation.WEAPON_HAND, WieldLocation.SHIELD_HAND):
                # can't keep a TWO handed weapon equipped if adding a 1h weapon or shield
                to_backpack = [slots[WieldLocation.TWO_HANDS]]
                slots[WieldLocation.TWO_HANDS] = None
                slots[use_slot] = obj

            elif use_slot is WieldLocation.BACKPACK:
                # belongs in the backpack, so goes back to it
                to_backpack = [obj]

            else:
                # replace whatever is in another equipment slot
                to_backpack = [slots[use_slot]]
                slots[use_slot] = obj

        except:
            raise equipmentError(f"Ye cannot move to a slot. You have fucked up now")

        for to_backpack_obj in to_backpack:
            # put stuff in backpack
            if to_backpack_obj:
                slots[WieldLocation.BACKPACK].append(to_backpack_obj)

        # store new state
        self._save()

    def all(self):
        """Get all objects in inventory regardless of location"""
        slots = self.slots
        inv = [
            (slots[WieldLocation.WEAPON_HAND], WieldLocation.WEAPON_HAND),
            (slots[WieldLocation.SHIELD_HAND], WieldLocation.SHIELD_HAND),
            (slots[WieldLocation.TWO_HANDS], WieldLocation.TWO_HANDS),
            (slots[WieldLocation.BODY], WieldLocation.BODY),
            (slots[WieldLocation.HEAD], WieldLocation.HEAD),
        ] + [(item, WieldLocation.BACKPACK) for item in slots[WieldLocation.BACKPACK]]
        return inv

    def inventory(self):
        """Returns a list of items in the inventory"""
        slots = self.slots
        if slots[WieldLocation.BACKPACK]:
            readout = []
            for item in slots[WieldLocation.BACKPACK]:
                readout += f"{item.key} : {item.size} slots"
            return "\n".join(readout)
        else:
            return "Yon backpack remain empty."

    def identify_slot(self, obj):
        """Returns what slot an item is currently in"""
        slots = self.slots
        for slot, slotobj in slots.items():
            if slotobj == obj:
                return slot

    def identify_loadout(self):
        """This returns all equipped items and their slots, but not the inventory."""

        slots = self.slots
        wielded = []
        for slot, slotobj in slots.items():
            if slot != WieldLocation.BACKPACK:
                wielded.append(slot, slotobj)
        if wielded:
            loadout = []
            for item in wielded:
                # slot, item
                loadout += f"{item[1]} : {item[2]}\n"
                return loadout
        else:
            return f"You're not wearing anything. How embarrassing!"

    @property
    def armor(self):
        slots = self.slots
        return sum(
            # armor is listed using it's defense, so remove 10
            # 11 is the base no-armor value
            getattr(slots[WieldLocation.BODY], "armor", 1),
            # shields and helmets are listed by their bonus to armor
            getattr(slots[WieldLocation.SHIELD_HAND], "armor", 0),
            getattr(slots[WieldLocation.HEAD], "armor", 0),
        )

    @property
    def weapon(self):
        # first checks 2h wield, then 1h; the two should never appear simultaneously
        slots = self.slots
        weapon = slots[WieldLocation.TWO_HANDS]
        if not weapon:
            weapon = slots[WieldLocation.WEAPON_HAND]
        if not weapon:
            return WeaponEmptyHand()
        return weapon

    def get_wearable_objects_from_backpack(self):
        """
        Get all wearable items (armor or helmets) from backpack. This is useful in order to
        have a list to select from when swapping your worn loadout.

        Returns:
            list: A list of objects with a suitable `inventory_use_slot`. We don't check
            quality, so this may include broken items (we may want to visually show them
            in the list after all).

        """
        return [
            obj
            for obj in self.slots[WieldLocation.BACKPACK]
            if obj.inventory_use_slot in (WieldLocation.BODY, WieldLocation.HEAD)
        ]

    def get_wieldable_objects_from_backpack(self):
        """
        Get all wieldable weapons (or spell runes) from backpack. This is useful in order to
        have a list to select from when swapping your wielded loadout.

        Returns:
            list: A list of objects with a suitable `inventory_use_slot`. We don't check
            quality, so this may include broken items (we may want to visually show them
            in the list after all).

        """
        return [
            obj
            for obj in self.slots[WieldLocation.BACKPACK]
            if obj.inventory_use_slot
            in (
                WieldLocation.WEAPON_HAND,
                WieldLocation.TWO_HANDS,
                WieldLocation.SHIELD_HAND,
            )
        ]

    def get_usable_objects_from_backpack(self):
        """
        Get all 'usable' items (like potions) from backpack. This is useful for getting a
        list to select from.

        Returns:
            list: A list of objects that are usable.

        """
        character = self.obj
        return [
            obj
            for obj in self.slots[WieldLocation.BACKPACK]
            if obj.at_pre_use(character)
        ]
