from unittest.mock import patch
from unittest.mock import Mock
from unittest.mock import MagicMock
from evennia.utils.test_resources import BaseEvenniaTest
from .. import rules
from ..enums import Ability
from .character import character

# leaving out the morale check test because it's just a roll against a static value
# don't feel like implementing another value into the WIP character class for that

class TestEvAdventureRuleEngine(BaseEvenniaTest):
    def setUp(self):
        # called before every test method
        super().setUp()
        self.roll_engine = rules.EvAdventureRollEngine()

    @patch("game.rules.randint")
    def test_roll(self, mock_randint):
        # tests a general roll, patching the random integer function to a
        # static number for consistency

        mock_randint.return_value = 4
        self.assertEqual(self.roll_engine.roll("1d6"), 4)
        self.assertEqual(self.roll_engine.roll("2d6"), 2 * 4)

    def test_advantage(self):
        # tests a roll with advantage

        adv = True
        disadv = False

        # sets up mock roll method, and automatically applies two results in order
        # this lets us set up controlled rolls without randomness in testing

        self.roll_engine.roll = Mock()
        
        # side effect allows us to create multiple different known results for a mocked object
        self.roll_engine.roll.side_effect = [4, 6]

        self.assertEqual(
            self.roll_engine.roll_adv_disadv(adv, disadv),
            6,
        )

    def test_disadvantage(self):
        # tests a roll with disadvantage

        adv = False
        disadv = True

        self.roll_engine.roll = Mock()
        self.roll_engine.roll.side_effect = [4, 6]

        self.assertEqual(
            self.roll_engine.roll_adv_disadv(adv, disadv),
            4,
        )

    def test_advantage_cancel(self):
        # tests a roll where advantage and disadvantage cancel out

        adv = True
        disadv = True

        self.roll_engine.roll = Mock()
        self.roll_engine.roll.side_effect = [6]

        self.assertEqual(
            self.roll_engine.roll_adv_disadv(adv, disadv),
            6,
        )

    # These tests use a very basic character I've set up in game.tests.character.py

    def test_pass_saving_throw(self):
        # tests a saving throw that passes

        # create a character object (WIP) to have a stat attribute
        char = character()
        char.strength = 16

        # mock rolls; keeping these arbitrarily low to prevent randomness
        self.roll_engine.roll_adv_disadv = Mock()
        self.roll_engine.roll_adv_disadv.side_effect = [2]

        # dis/advantage not needed, defaults argument to false if left out
        self.assertEqual(
            self.roll_engine.saving_throw(char, Ability.STR, 15), (True, None)
        )

    def test_fail_saving_throw(self):
        # tests a saving throw that fails

        char = character()
        char.strength = 12

        advantage = False
        disadvantage = False

        self.roll_engine.roll = Mock()
        self.roll_engine.roll.side_effect = [2]

        self.assertEqual(
            self.roll_engine.saving_throw(char, Ability.STR, 15), (False, None)
        )

    def test_pass_saving_throw_but_with_patch(self):
        # I wanna try a patch this time. There are benefits to using patches.
        # Patches stop mocked classes from staying instantiated, that is, their value is not reset.
        # Patches clean themselves up after a test, unlike a mock.
        # This is mostly important when overwriting functions, classes and modules, in a test.
        # Instanced objects are fine to mock, but good to keep in mind.
        # For example, look at the two tests above. Can you work out the difference in the rolls?

        char = character()
        char.strength = 16

        with patch("game.rules.EvAdventureRollEngine.roll_adv_disadv", return_value=2):
            self.assertEqual(
                self.roll_engine.saving_throw(char, Ability.STR, 15), (True, None)
            )
    
    @patch("game.rules.EvAdventureRollEngine.saving_throw")
    def test_pass_opposed_saving_throw(self, mock_saves):
        # testing an opposed saving throw that passes
        
        # saving_throw returns a tuple
        # tuples are iterable, and thus usable as a side effect
        mock_saves.side_effect = {( True, None )}
        
        # instantiate characters with different stats to pass or fail 
        char1 = character()
        char1.strength = 16
        char2 = character()
        char2.strength = 15
        
        self.assertEqual(self.roll_engine.opposed_saving_throw(char1, char2, Ability.STR, Ability.STR, False, False), (True, None))
    
    @patch("game.rules.EvAdventureRollEngine.saving_throw")
    def test_fail_opposed_saving_throw(self, mock_saves):
        
        mock_saves.side_effect = {( False, None )}
        
        char1 = character()
        char1.strength = 15
        char2 = character()
        char2.strength = 16
        
        self.assertEqual(self.roll_engine.opposed_saving_throw(char1, char2, Ability.STR, Ability.STR, False, False), (False, None))
    
    @patch("game.rules.EvAdventureRollEngine.roll")
    def test_heal_from_rest(self, mocki_roll):
        # testing the heal logic
        
        mocki_roll.return_value = 3
        
        char = character()
        char.endurance = 3
        
        self.assertEqual(self.roll_engine.heal_from_rest(char), 6)
        
    @patch("game.rules.EvAdventureRollEngine.roll")
    def test_roll_random_table_items(self, mock_roll):
        # testing random roll table function for different item ranges
        mock_roll.return_value = 3
        
        table = [("1-5", "item" ),("6-10", "item2")]
        
        self.assertEqual(self.roll_engine.roll_random_table("1d20", table), "item")
        
        mock_roll.return_value = 6
        
        self.assertEqual(self.roll_engine.roll_random_table("1d20", table), "item2")
    
    @patch("game.rules.EvAdventureRollEngine.roll")    
    def test_roll_random_table_error(self,mock_roll):
        # testing random roll table function for items not in table
        mock_roll.return_value = 20
        
        table = [("1-5", "item" ),("6-10", "item2")]
        
        # here, we're testing if using the wrong inputs raises a specific runtime error
        # this is useful, because if a func has multiple runtime error possibilities,
        # we might end up with a runtime error we didn't expect to be testing for
        
        with self.assertRaises(RuntimeError) as err:
            self.roll_engine.roll_random_table("1d20", table)
            self.assertEqual(err.message, "roll_random_table: Invalid die roll")
        self.assertTrue(
            str(err.exception).startswith("roll_random_table: Invalid die roll"), err.exception
        )