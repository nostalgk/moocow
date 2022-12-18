from evennia import DefaultCharacter, AttributeProperty
from .rules import dice


class LivingMixin:

    is_pc = False

    def heal(self, hp):
        """
        Heal hp amount of health, not allowing to exceed our max hp

        """
        damage = self.hp_max - self.hp
        healed = min(damage, hp)
        self.hp += healed

        self.msg(f"You heal for {healed} HP.")

    def at_pay(self, amount):
        """When paying coins, make sure to never detract more than we have"""
        amount = min(amount, self.coins)
        self.coins -= amount
        return amount

    def at_damage(self, damage, attacker=None):
        """Called when attacked and taking damage"""
        self.hp -= damage

    def at_defeat(self):
        """Called when defeated. By default this means death."""
        self.at_death()

    def at_death(self):
        """Called when this thing dies."""
        # this will mean different things for different living things
        pass

    def at_do_loot(self, looted):
        """Called when looting another entity"""
        looted.at_looted(self)

    def at_looted(self, looter):
        """Called when looted by another entity"""

        # default to stealing some coins
        max_steal = dice.roll("1d10")
        stolen = self.at_pay(max_steal)
        looter.coins += stolen


class EvAdventureCharacter(LivingMixin, DefaultCharacter):
    """A character to use for our game."""

    is_pc = True

    strength = AttributeProperty(1)
    dexterity = AttributeProperty(1)
    endurance = AttributeProperty(1)
    perception = AttributeProperty(1)
    intelligence = AttributeProperty(1)
    willpower = AttributeProperty(1)

    hp = AttributeProperty(8)
    hp_max = AttributeProperty(8)

    level = AttributeProperty(1)
    xp = AttributeProperty(0)
    coins = AttributeProperty(0)

    def at_defeat(self):
        """Characters roll on death table"""
        if self.location.allow_death:
            # this allows rooms to have nonlethal battles
            dice.roll_death(self)
        else:
            self.location.msg_contents(
                f"$You() $conj(collapse) in a heap, alive but beaten.", from_obj=self
            )
            self.heal(self.hp_max)

    def at_death(self):
        """We rolled 'dead' on the death table."""
        self.location.msg_contents(
            "$You() collapse in a heap, embraced by death.", from_obj=self
        )
        # TODO - go back into chargen to make a new character!


### example of use
#class Character(DefaultCharacter):
#
#    strength = AttributeProperty(10, category="stat")
#    constitution = AttributeProperty(11, category="stat")
#    agility = AttributeProperty(12, category="stat")
#    magic = AttributeProperty(13, category="stat")
#
#    sleepy = AttributeProperty(False, autocreate=False)
#    poisoned = AttributeProperty(False, autocreate=False)
#
#    """
#    char = create_object(Character)
#
#    char.strength   # returns 10
#    char.agility = 15  # assign a new value (category remains 'stat')
#
#    char.db.magic  # returns None (wrong category)
#    char.attributes.get("agility", category="stat")  # returns 15
#
#    char.db.sleepy # returns None because autocreate=False (see below)
#    
#    char.sleepy   # returns False, no db access
#
#    char.db.sleepy   # returns None - no Attribute exists
#    char.attributes.get("sleepy")  # returns None too
#
#    char.sleepy = True  # now an Attribute is created
#    char.db.sleepy   # now returns True!
#    char.attributes.get("sleepy")  # now returns True
#
#    char.sleepy  # now returns True, involves db access
#    """
#