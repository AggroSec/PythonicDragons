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

    def test_can_use_ability(self):
        player = Player(1, 10, 10, 10, 10, 10, 10, 10, 10, "Jack, of the Trades", "1d6", {"1": 1, "2":0}, "saber", ["swing", "slice", "stab"])
        player.add_ability(
            {
            "name": "Singing Heal",
            "description": "During travels doing trades, you have learned to sing a healing song of magic",
            "uses_per_rest": 0,
            "modifier_stat": "wisdom",
            "attack_descs": [
                "Singing out in a loud voice, (a) enunciates, 'glory be, look at me, heal me with sing'"
            ],
            "attack_misses": [
                "N/A"
            ],
            "effects": [
                {
                "type": "spell_heal",
                "value": "1d8",
                "spell_slot_level": 1,
                "target": "ally"
                }
            ]
            }
        )
        player.add_ability(
            {
            "name": "Singing Heal II",
            "description": "During travels doing trades, you have learned to sing a healing song of magic",
            "uses_per_rest": 0,
            "modifier_stat": "wisdom",
            "attack_descs": [
                "Singing out in a loud voice, (a) enunciates, 'glory be, look at me, heal me with sing'"
            ],
            "attack_misses": [
                "N/A"
            ],
            "effects": [
                {
                "type": "spell_heal",
                "value": "2d8",
                "spell_slot_level": 2,
                "target": "ally"
                }
            ]
            }
        )
        player.add_ability(
            {
            "name": "Derp Heal",
            "description": "During travels doing trades, you have learned to sing a healing song of magic",
            "uses_per_rest": 0,
            "modifier_stat": "wisdom",
            "attack_descs": [
                "Singing out in a loud voice, (a) enunciates, 'glory be, look at me, heal me with sing'"
            ],
            "attack_misses": [
                "N/A"
            ],
            "effects": [
                {
                "type": "spell_heal",
                "value": "1d4",
                "spell_slot_level": 0,
                "target": "ally"
                }
            ]
            }
        )
        player.rest_usage["Power Swing II"] = 3
        player.rest_usage["Power Swing"] = 2
        player.add_ability(
            {
            "name": "Power Swing",
            "description": "During travels doing trades, you have learned to put some oomph in your weapon attacks",
            "uses_per_rest": 3,
            "modifier_stat": "physical",
            "attack_descs": [
                "Singing out in a loud voice, (a) enunciates, 'glory be, look at me, put some OOMPH in this swing' as he swings his weapon at (t)"
            ],
            "attack_misses": [
                "N/A"
            ],
            "effects": [
                {
                "type": "damage",
                "value": "1d12",
                "target": "enemy"
                }
            ]
            }
        )
        player.add_ability(
            {
            "name": "Power Swing II",
            "description": "During travels doing trades, you have learned to put some oomph in your weapon attacks",
            "uses_per_rest": 3,
            "modifier_stat": "physical",
            "attack_descs": [
                "Singing out in a loud voice, (a) enunciates, 'glory be, look at me, put some OOMPH in this swing' as he swings his weapon at (t)"
            ],
            "attack_misses": [
                "N/A"
            ],
            "effects": [
                {
                "type": "damage",
                "value": "1d12",
                "target": "enemy"
                }
            ]
            }
        )
        basic_attack = can_use_ability(player, "Basic Attack")
        sing_heal = can_use_ability(player, "Singing Heal")
        sing_heal_ii = can_use_ability(player, "Singing Heal II")
        derp_heal = can_use_ability(player, "Derp Heal")
        power_swing = can_use_ability(player, "Power Swing")
        power_swing_ii = can_use_ability(player, "Power Swing II")
        self.assertEqual(basic_attack, True)
        self.assertEqual(sing_heal, True)
        self.assertEqual(sing_heal_ii, False)
        self.assertEqual(derp_heal, True)
        self.assertEqual(power_swing, True)
        self.assertEqual(power_swing_ii, False)