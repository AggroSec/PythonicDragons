from dice import *
from character import *
from tabulate import tabulate

def run_combat(player, enemies=[]):
    '''
    TLDR: no bonus actions at this point.

    Some caveats for the MVP code, and it will be stated in the readme, this is not a 1 to 1 translation of DnD rules, just heavily inspired by it.
    If this project takes off, people want things added, I come back to improve when I have more time I'll add things like bonus actions. For now to keep
    it simple this is one of the few things that will be left out/changed from actual DnD rules
    '''

    log_event("Combat has been initiated!")
    initiative = roll_initiative(player, enemies)
    turn_order = get_turn_order(initiative)
    current_round = 1
    log_event(f"Initiatives have been determined: {turn_order}")

def handle_player_turn(player, enemies):
    choices = [ability["name"] for ability in player.abilities]
    action = player_choice("It's your move, what do you choose(number|info [num])?", choices, player)
    log_event(f"You have chosen to use: {action}")
    target = select_target(player, enemies, action)
    use_ability(player, target, action)

def select_target(targeter: Character, enemies: list[Character], ability_name):
    #multiple allies not implemented, so if skill targets ally, it will ignore enemies
    ability_info = {}
    for ability in targeter.abilities:
        if ability["name"] == ability_name:
            ability_info = ability
    first_effect = ability["effects"][0]
    if first_effect["target"] == "ally":
        return targeter
    elif first_effect["target"] == "enemy":
        enemy_list = [enemy.name for enemy in enemies]
        enemy_name =player_choice("Who are you targeting(number)?", enemy_list, targeter, selecting_target=True)
        for enemy in enemies:
            if enemy.name == enemy_name:
                return enemy

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

def player_choice(prompt, choices=[], player=None, selecting_target=False):
    '''again thinking of future extensiblity, for now takes what the caller wants to prompt the user, and valid choices,
    and validates the player choice before returning the choice. if not valid, prompts to pick again until a valid choice is given'''
    print(prompt)
    for i, opt in enumerate(choices, 1):
        print(f"[{i}] {opt}")
    while True:
        try:
            choice = input("What is your choice? ").strip().lower()
            if "info" in choice:
                info_choice = choice.replace("info", "").strip()
                if 1 <= int(info_choice) <= len(choices):
                    ability_name = choices[int(info_choice)-1]
                    show_ability_info(ability_name, player)
                    continue
                else:
                    raise ValueError
            if 1 <= int(choice) <= len(choices):
                if selecting_target:
                    return choices[int(choice)-1]
                elif can_use_ability(player, choices[int(choice)-1]):
                    return choices[int(choice)-1]
                else:
                    raise ValueError
            else:
                print(f"Choice must be between 1 and {len(choices)}")
        except ValueError:
            print("Invalid choice, try again!")

def can_use_ability(player, ability_name):
    chosen_ability = {}
    can_use = True
    for ability in player.abilities:
        if ability["name"] == ability_name:
            chosen_ability = ability
    if not chosen_ability:
        raise ValueError("how did it get to this, should be a valid ability...")
    if ability_name in player.rest_usage:
        times_used = player.rest_usage[ability_name]
        if chosen_ability["uses_per_rest"] > 0 and times_used >= chosen_ability["uses_per_rest"]:
            can_use = False
            log_event(f"{ability_name} is on cooldown until next rest.")
    for effect in chosen_ability["effects"]:
        if effect["type"].startswith("spell_"):
            spell_slot = str(effect["spell_slot_level"])
            if spell_slot != "0" and (player.spell_slots[spell_slot] == 0 or spell_slot not in player.spell_slots):
                can_use = False
                log_event(f"Not enough spell slots for {ability_name}")
    return can_use
    

def use_ability(ability_user: Character, target: Character, ability_name=""):
    pass

def show_ability_info(name, player):
    for ability in player.abilities:
        if ability["name"] == name:
            log_event(f"Ability: {ability['name']}")
            log_event(f"Description: {ability.get('description', 'No description available')}")
            if ability["uses_per_rest"] != 0:
                log_event(f"Total uses before rest: {ability['uses_per_rest']}")
            log_event(f"Modifier Stat: {ability['modifier_stat']}")
            log_event("\n Effects:")
            effects_data = []
            for effect in ability['effects']:
                effects_data.append([
                    effect.get("type", "Unknown"),
                    effect.get("value", "N/A"),
                    effect.get("target", "N/A"),
                    effect.get("spell_slot_level", "N/A"),
                    effect.get("stat", "N/A"),
                    effect.get("duration", "N/A")
                ])
            log_event(tabulate(effects_data, headers=["Type", "Value", "Target", "Spell Slot Level", "Effected Stat", "Duration"],tablefmt="fancy_grid"))

player = Player(1, 10, 16, 16, 12, 10, 8, 8, 15, "AggroSec", "2d6", {"1": 0}, "Greataxe", ["swing", "chop", "cleave"])
new_ability = {
  "name": "Smite Evil",
  "description": "Strike with holy power, harming and weakening undead",
  "uses_per_rest": 1,
  "modifier_stat": "wisdom",
  "attack_descs": [
    "You pray to the heavens, and as you strike a holy bolt from the sky flies with you, smiting %t"
  ],
  "attack_misses": [
    "You pray for smiting power, but there is no answer... Silence fills the void."
  ],
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
      "spell_slot_level": 0,
      "target": "enemy"
    }
  ]
}
player.add_ability(new_ability)
enemy1 = EnemyNPC(1,1,1,1,1,1,1,1,12,"Bob the minion","1d2",10)
enemy2 = EnemyNPC(1,1,1,1,1,1,1,1,12,"Bob the chieftain","1d6",50)
choices = [ability["name"] for ability in player.abilities]
action = player_choice("It's your move, what do you choose?", choices, player, selecting_target=False)
log_event(f"You have chosen to use: {action}")
target = select_target(player, [enemy1,enemy2], action)
log_event(f"target info: {target.name}, HP:{target.current_hp}, AC:{target.ac}")