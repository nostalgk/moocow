from unittest.mock import patch
from unittest.mock import Mock
from unittest.mock import MagicMock
from evennia.utils.test_resources import BaseEvenniaTest
from .. import rules
from ..enums import Ability
from .character import character


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

        # create character class
        
        char = character()
        char.strength = 16
        
        # mock rolls; keeping these arbitrarily low to prevent randomness
        self.roll_engine.roll_adv_disadv = Mock()
        self.roll_engine.roll_adv_disadv.side_effect = [2]

        # dis/advantage not needed, defaults argument to false if left out
        self.assertEqual(self.roll_engine.saving_throw(char, Ability.STR, 15), (True, None))

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
        # This is mostly important when overwriting functions, classes and modules, in a test
        # Instanced objects are fine to mock, but good to keep in mind.
        # For example, look at the two tests above. Can you work out the difference in the rolls?

        char = character()
        
        with patch('game.rules.EvAdventureRollEngine.roll_adv_disadv', return_value = 2):
            self.assertEqual(self.roll_engine.saving_throw(char, Ability.STR, 15), (True, None))
