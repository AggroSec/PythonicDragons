from engine.character import *
from engine.dice import *
from engine.combat import *
import unittest

class TestCombat(unittest.TestCase):
    
    def test_initiative(self):
        player = Player(1, 10, 16, 16, 12, 10, 8, 8, 15, "AggroSec", "2d6", {})
        enemy1 = EnemyNPC(1, 5, 10, 8, 6, 8, 8, 8, 8, "Goblin", "1d4", 0)
        enemy2 = EnemyNPC(1, 3, 10, 8, 16, 8, 8, 8, 8, "Goblin Skirmisher", "1d4", 0)
        initiative_rolls = roll_initiative(player, [enemy1, enemy2])
        print(initiative_rolls)
        self.assertEqual(len(initiative_rolls), 3)

    def test_get_turn_order(self):
        initiative_dict = {"AggroSec": 15, "Speedster": 22, "Gobbo": 3}
        turn_order = get_turn_order(initiative_dict)
        print(turn_order)
        self.assertEqual(turn_order, ["Speedster", "AggroSec", "Gobbo"])