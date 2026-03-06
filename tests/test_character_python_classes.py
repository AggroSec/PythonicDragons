from engine.character import *
from engine.dice import *
import unittest

class TestCharacters(unittest.TestCase):

    def test_base_character(self):
        vanilla = Character(1, 10, 10, 10, 10, 10, 10, 10, 10, "1d4")
        print("base character created")
        self.assertEqual(vanilla.current_hp, vanilla.max_hp)
        self.assertEqual(vanilla.ac, 10)
        print(f"taking 10 damage, current hp: {vanilla.current_hp}")
        vanilla.damage_hp(2)
        self.assertEqual(vanilla.current_hp, 8)
        print(f"current_hp after damage: {vanilla.current_hp}")
        vanilla.heal_hp(1)
        self.assertEqual(vanilla.current_hp, 9)
        print(f"healed for 1, current_hp: {vanilla.current_hp}")
        vanilla.heal_hp(10)
        self.assertEqual(vanilla.current_hp, 10)
        print(f"over healed, current_hp: {vanilla.current_hp}")
        vanilla.damage_hp(50)
        self.assertEqual(vanilla.current_hp, 0)
        print(f"oneshotted, current_hp: {vanilla.current_hp}")
        num_die = vanilla.basic_attack["num_die"]
        sides = vanilla.basic_attack["sides"]
        attack_roll, _ = dice_roller(sides, num_die)
        self.assertTrue(1 <= attack_roll <= 4)
        print(f"attack roll: {attack_roll}")

    def test_player_character(self):
        player = Player(2, 12, 12, 10, 14, 10, 10, 18, 10, "AggroSec", "2d6")
        print(f"===The Harrowing Trial of {player.name}===")
        print(f"{player.name} started this journey at a healthy {player.current_hp} hp")
        self.assertEqual(player.current_hp, 21)
        print(f"His armor was light but his dex afforded him a modest AC of {player.ac}")
        self.assertEqual(player.ac, 12)
        print(f"The adventures were many and myriad, from a humble start of slaying goblins, to slaying the dreaded pythonic dragon, leveling up and finding better gear along the way")
        player.level = 10
        player.update_level_health()
        player.dex = 18
        player.update_player_ac(18, 3)
        print(f"Though his dexterity was improved, his armor limited his AC to {player.ac} but he had plenty of health({player.max_hp}) to back up this slight draw back.")
        self.assertTrue(player.max_hp > 21)
        self.assertTrue(player.ac, 21)
        player.update_player_ac(10, 20)
        player.current_hp = player.max_hp
        player.damage_hp(5)
        print(f"However, he was caught off-guard one day, the smell of smoke waking him from slumber, he forgot his special AC armor! This was bad, but he could use his limber body to avoid blows still (AC:{player.ac}).")
        self.assertEqual(player.ac, 14)
        print(f"It was not enough though, to completely avoid the fire at his door as he charged out the house to see the cause (HEALTH:{player.current_hp}).")
        self.assertEqual(player.max_hp - 5, player.current_hp)
        print(f"What he saw struck him with fear and rage, as a... TO BE CONTINUED")

    def test_bob_the_minion(self):
        enemy = EnemyNPC(1, 8, 6, 8, 8, 18, 10, 20, 8, "Bob the minion", "1d2", 50)
        print(f"####{enemy.name}'s sad life####")
        print(f"{enemy.name} was a simple goblin, he never was good at much anything goblins do: he wasn't the strongest at swinging a dagger, he always trip of seemingly nothing, and he didn't have the best health({enemy.max_hp})")
        self.assertEqual(enemy.max_hp, 8)
        print(f"He was an odd goblin, always reading books({enemy.intel}), and giving speeches({enemy.ris}), trying to change his tribe from bloodthirsty hooligans to a more civilized existence")
        self.assertEqual(enemy.get_modifier(enemy.intel), 4)
        print(f"One day, he encountered an adventurer just starting out on her journey. She mistook {enemy.name} as any ol' goblin to slay.")
        print(f"She had almost beat poor {enemy.name} to a pulp, when the anger finally burst forth!")
        ability_roll, roll_list = dice_roller(100)
        print(f"HIDDEN ABILITY ROLL: {roll_list}")
        if ability_roll < enemy.ability_use_chance:
            ability_attack_string = f"{enemy.name} unleashed his goblin rage in a fit of magical energy, burning the young adventurer in hell-fire flames"
            ability_ending = f"It was this day, {enemy.name} discovered his abilities, becoming chieftain of his tribe. He civilized them, and ruled with fear and cunning."
        else:
            ability_attack_string = f"His rage wasn't enough, and as quickly as he felt it, it fizzed out"
            ability_ending = f"With a gleam in her eyes, the adventurer delivered the final blow to poor {enemy.name}...\n'What luck!' said the adventurer, 'That goblin was work more xp than the others!'"
        print(ability_attack_string)
        print(ability_ending)
        self.assertTrue(ability_attack_string)

    def test_player_basic_attack_ability(self):
        player = Player(2, 12, 12, 10, 14, 10, 10, 18, 10, "AggroSec", "2d6")
        print(player.abilities)
        self.assertTrue("Basic Attack" == player.abilities[0]["name"])


