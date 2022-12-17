from evennia.utils import create
from evennia.utils.test_resources import BaseEvenniaTest 

from ..characters import EvAdventureCharacter 

class TestCharacters(BaseEvenniaTest):
    def setUp(self):
        super().setUp()
        self.character = create.create_object(EvAdventureCharacter, key="testchar")

    def test_heal(self):
        self.character.hp = 0 
        self.character.hp_max = 8 
        
        self.character.heal(1)
        self.assertEqual(self.character.hp, 1)
        # make sure we can't heal more than max
        self.character.heal(100)
        self.assertEqual(self.character.hp, 8)
        
    def test_at_pay(self):
        self.character.coins = 100 
        
        result = self.character.at_pay(60)
        self.assertEqual(result, 60) 
        self.assertEqual(self.character.coins, 40)
        
        # can't get more coins than we have 
        result = self.character.at_pay(100)
        self.assertEqual(result, 40)
        self.assertEqual(self.character.coins, 0)
        
    # tests for other methods ... 