from unittest.mock import Mock, patch
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
    
    @patch("game.rules.EvAdventureRollEngine.roll")
    def test_at_looted(self, mach_roll):
        mach_roll.return_value = 7
        char2 = create.create_object(EvAdventureCharacter, key="looted")
        char2.coins = 20
        
        char2.at_looted(self.character)
        
        self.assertEqual(self.character.coins, 7)
        
    # rooms need to be created before this can work    
    
    #def test_at_defeat_pc_survive(self):
    #    self.character.hp = 0
    #    self.character.max_hp = 10
    #    
    #    self.character.at_defeat()
    #    
    #    self.assertEqual(self.character.hp, 10)
        
        
    # tests for other methods ... 