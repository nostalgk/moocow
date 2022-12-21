from unittest.mock import Mock, patch
from evennia.utils import create
from evennia.utils.test_resources import BaseEvenniaTest
from ..objects import EvAdventureConsumable
from ..characters import EvAdventureCharacter


class TestObjects(BaseEvenniaTest):
    def setUp(self):
        super().setUp()
        self.consumable = create.create_object(EvAdventureConsumable, key="testconsum")
        self.character = create.create_object(EvAdventureCharacter, key="testchar")

    def test_pre_use(self):
        # normally, "" would be a character object, but this method doesn't operate a character rn

        self.consumable.uses = 0

        self.assertEqual(self.consumable.at_pre_use(self.character), False)

    def test_post_use(self):

        self.consumable.uses = 1

        result = self.consumable.at_post_use(self.character)

        self.assertTrue(result.startswith("testconsum"))

# pretty much all these is here for now lol