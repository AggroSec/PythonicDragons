from dice import *
from character import *

def run_combat(player, enemies=[]):
    '''
    TLDR: no bonus actions at this point.

    some caveats for the MVP code, and it will be stated in the readme, this is not a 1 to 1 translation of DnD rules, just heavily inspired by it.
    If this project takes off, people want things added, I come back to improve when I have more time I'll add things like bonus actions. for now to keep
    it simple this is one of the few things that will be left out/changed from actual DnD rules
    '''

    log_event("Combat has been initiated!")
    initiative = roll_initiative(player, enemies)
    turn_order = get_turn_order(initiative)
    current_round = 1
    log_event(f"Initiatives have been determined: {turn_order}")

def handle_player_turn(player):
    choices = [ability["name"] for ability in player.abilities]
    action = player_choice("It's your move, what do you choose?", choices)
    log_event(f"You have chosen to use: {action}")

def get_turn_order(initiative_dict):
    # separation to future proof for mid combat initiative changes. currently not handling ties, the turns fall how the sorted function sorts
    return sorted(initiative_dict, key=initiative_dict.get, reverse=True)

def roll_initiative(player, enemies=[]):
    initiative_rolls = {}
    log_event("Let us roll for initiative!")
    player_initiative, actual_roll = dice_roller(20, 1, player.get_modifier(player.dex))
    initiative_rolls[player.name] = player_initiative
    log_event(f"{player.name} rolled a {player_initiative}({actual_roll}+{player.get_modifier(player.dex)})")
    for enemy in enemies:
        initiative_roll, actual_roll = dice_roller(20, 1, enemy.get_modifier(enemy.dex))
        initiative_rolls[enemy.name] = initiative_roll
        log_event(f"{enemy.name} rolled a {initiative_roll}({actual_roll}+{enemy.get_modifier(enemy.dex)})")
    return initiative_rolls


def log_event(message):
    '''currently just prints to console, can be extended to work with GUI or TUI (hopefully) without effecting combat logic'''
    print(message)

def player_choice(prompt, choices=[]):
    '''again thinking of future extensiblity, for now takes what the caller wants to prompt the user, and valid choices,
    and validates the player choice before returning the choice. if not valid, prompts to pick again until a valid choice is given'''
    print(prompt)
    for i, opt in enumerate(choices, 1):
        print(f"[{i}] {opt}")
    while True:
        try:
            choice = int(input("What is your choice (number)? "))
            if 1 <= choice <= len(choices):
                return choices[choice-1]
            else:
                print(f"Choice must be between 1 and {len(choices)}")
        except ValueError:
            print("Invalid choice, try again!")

player = Player(1, 10, 16, 16, 12, 10, 8, 8, 15, "AggroSec", "2d6", {})
new_ability = {
  "name": "Smite Evil",
  "description": "Strike with holy power, harming and weakening undead",
  "uses_per_rest": 1,
  "modifier_stat": "wisdom",
  "effects": [
    {
      "type": "spell_damage",
      "value": "2d8",
      "spell_slot_level": 1,
      "target": "enemy",
      "extra": {"damage_type": "radiant"}
    },
    {
      "type": "spell_debuff",
      "stat": "attack_bonus",
      "value": -2,
      "duration": 2,
      "spell_slot_level": 1,
      "target": "enemy"
    }
  ]
}
player.add_ability(new_ability)
handle_player_turn(player)