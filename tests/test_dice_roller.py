from engine.dice import *
import unittest

class TestDiceRoller(unittest.TestCase):

    def test_roll_with_modifier(self):
        roll, roll_list = dice_roller(20, modifier=3)
        print(f"d20 single roll with 3 as modifier: {roll_list} -> {roll}")
        self.assertEqual(roll, roll_list[0] + 3)
    
    def test_roll_without_catching_list(self):
        roll, _ = dice_roller(6)
        print(f"d6 roll without fancy list or modifiers: {roll}")
        self.assertTrue(1 <= roll <= 6)

    def test_advantage(self):
        roll, roll_list = dice_roller(20, modifier=1, advantage=True)
        print(f"ADVANTAGE ROLL: d20 + 1 modifier: {roll_list} -> {roll}")
        advantage_die = max(roll_list)
        self.assertEqual(roll, advantage_die + 1)

    def test_disadvantage(self):
        roll, roll_list = dice_roller(20, modifier=2, disadvantage=True)
        print(f"DISADVANTAGE ROLL: d20 + 2 modifier: {roll_list} -> {roll}")
        disadvantage_die = min(roll_list)
        self.assertEqual(roll, disadvantage_die + 2)
    
    def test_advantage_and_disadvantage(self):
        roll, roll_list = dice_roller(20, modifier=4, advantage=True, disadvantage=True)
        print(f"testing advantage cancel for d20 + 4: {roll_list} -> {roll}")
        self.assertEqual(len(roll_list), 1)

    def test_multi_dice_damage_roll(self):
        roll, roll_list = dice_roller(8, 3, 4)
        print(f"FIREBALL DAMAGE: 3d8 + 4 roll - {roll_list} -> {roll}")
        roll_sum = sum(roll_list)
        self.assertEqual(roll, roll_sum + 4)