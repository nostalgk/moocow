from unittest.mock import patch
from unittest.mock import Mock
from unittest.mock import MagicMock
from evennia.utils.test_resources import BaseEvenniaTest
from .. import rules



class TestEvAdventureRuleEngine(BaseEvenniaTest):
    
    def setUp(self):
        # called before every test method
        super().setUp()
        self.roll_engine = rules.EvAdventureRollEngine()
    
    @patch("game.rules.randint")
    def test_roll(self, mock_randint):
        mock_randint.return_value = 4
        self.assertEqual(self.roll_engine.roll("1d6"), 4)
        self.assertEqual(self.roll_engine.roll("2d6"), 2 * 4)
    
    @patch("game.rules.EvAdventureRollEngine.roll", side_effect=[4, 6])
    def test_advantage(self, advantage=True, disadvantage=False):
        self.assertEqual(advantage, True)
        self.assertEqual(self.roll_engine.roll_with_advantage_or_disadvantage(True, False), 6)
        