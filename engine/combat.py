from dice import *
from character import *
from tabulate import tabulate
import random, uuid

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
    if player != target:
        status_update(player, target)

def status_update(player, target):
    target_hp_percent = (target.current_hp/target.max_hp) * 100
    if target_hp_percent >= 75:
        log_event(f"{target.name} looks fresh and ready for a fight — barely a scratch on them.")
    elif target_hp_percent < 75 and target_hp_percent >= 50:
        log_event(f"{target.name} is breathing harder now, a few cuts and bruises showing through, but they're still standing strong.")
    elif target_hp_percent < 50 and target_hp_percent >= 25:
        log_event(f"{target.name} is faltering — bloodied, staggering a little, but clinging to the fight with grim determination.")
    elif target_hp_percent < 25 and target_hp_percent > 0:
        log_event(f"{target.name} is on the verge of collapse — swaying, gasping, one good hit away from going down.")
    elif target_hp_percent <= 0:
        log_event(f"{target.name} collapses lifelessly to the ground — the fight has left them.")

def select_target(targeter: Character, enemies: list[Character], ability_name):
    #multiple allies not implemented, so if skill targets ally, it will ignore enemies
    ability_info = {}
    for ability in targeter.abilities:
        if ability["name"] == ability_name:
            ability_info = ability
    first_effect = ability_info["effects"][0]
    if first_effect["target"] == "ally": # have a bug that needs to be squashed when we come back to this.
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
    ability_hits = False
    if ability_user == target:
        ability_hits = True
        _, does_crit = attack_roll(ability_user, target, ability_name) #we'll let heals crit for now, we may just make it auto no crit. heals will still always hit
    else:
        ability_hits, does_crit = attack_roll(ability_user, target, ability_name)
    if ability_hits:
        if does_crit:
            log_event(f"attack roll was a CRIT!")
        handle_effects(ability_user, target, ability_name, does_crit)
        for ability in ability_user.abilities:
            if ability_name == ability["name"]:
                ability_hit_lines = ability["attack_descs"]
        hit_line = random.choice(ability_hit_lines)
        hit_line = hit_line.replace("(v)", random.choice(ability_user.weapon_verb)).replace("(a)", ability_user.name).replace("(t)", target.name)
        log_event(hit_line)
    else:
        for ability in ability_user.abilities:
            if ability_name == ability["name"]:
                ability_misses = ability["attack_misses"]
        miss_string = random.choice(ability_misses)
        miss_string = miss_string.replace("(v)", random.choice(ability_user.weapon_verb)).replace("(a)", ability_user.name).replace("(t)", target.name)
        log_event(f"MISS! {miss_string}")

def handle_effects(user, target, ability_name, does_crit):
    for ability in user.abilities:
        if ability_name == ability["name"]:
            used_ability = ability
            ability_effects = ability["effects"]
            stat_mod = find_stat_mod(user, ability["modifier_stat"])
    handle_rest_per_use(used_ability, user)
    for effect in ability_effects:
        match effect["type"]:
            case "damage":
                attack_string = effect["value"]
                split_attack_string = attack_string.split("d")
                if len(split_attack_string) == 1:
                    damage = int(attack_string)
                    target.damage_hp(damage)
                    log_event(f"{damage} was dealt to {target.name}")
                elif len(split_attack_string) == 2:
                    die_num = int(split_attack_string[0])
                    die_sides = int(split_attack_string[1])
                    damage, roll_list = dice_roller(die_sides, die_num, stat_mod)
                    if does_crit:
                        damage *= 2
                    target.damage_hp(damage)
                    log_event(f"{damage}({roll_list}+{stat_mod}) was dealt to {target.name}")
                else:
                    raise ValueError("proper attack string was not provided in json data")
            case "spell_damage":
                handle_spell_slots(effect, user)
                attack_string = effect["value"]
                split_attack_string = attack_string.split("d")
                if len(split_attack_string) == 1:
                    damage = int(attack_string)
                    target.damage_hp(damage)
                    log_event(f"{damage} was dealt to {target.name}")
                elif len(split_attack_string) == 2:
                    die_num = int(split_attack_string[0])
                    die_sides = int(split_attack_string[1])
                    damage, roll_list = dice_roller(die_sides, die_num, stat_mod)
                    if does_crit:
                        damage *= 2
                    target.damage_hp(damage)
                    log_event(f"{damage}({roll_list}+{stat_mod}) was dealt to {target.name}")
                else:
                    raise ValueError("proper attack string was not provided in json data")
            case "heal":
                heal_string = effect["value"]
                split_heal_string = heal_string.split("d")
                if len(split_heal_string) == 1:
                    heal_amount = int(heal_string)
                    target.heal_hp(heal_amount)
                    log_event(f"{target.name} has been healed for {heal_amount}")
                elif len(split_heal_string) == 2:
                    die_num = int(split_heal_string[0])
                    die_sides = int(split_heal_string[1])
                    heal, roll_list = dice_roller(die_sides, die_num, stat_mod)
                    if does_crit:
                        heal *= 2
                    target.heal_hp(heal)
                    log_event(f"{target.name} was healed for {heal}({roll_list}+{stat_mod})")
            case "spell_heal":
                handle_spell_slots(effect, user)
                heal_string = effect["value"]
                split_heal_string = heal_string.split("d")
                if len(split_heal_string) == 1:
                    heal_amount = int(heal_string)
                    target.heal_hp(heal_amount)
                    log_event(f"{target.name} has been healed for {heal_amount}")
                elif len(split_heal_string) == 2:
                    die_num = int(split_heal_string[0])
                    die_sides = int(split_heal_string[1])
                    heal, roll_list = dice_roller(die_sides, die_num, stat_mod)
                    if does_crit:
                        heal *= 2
                    target.heal_hp(heal)
                    log_event(f"{target.name} was healed for {heal}({roll_list}+{stat_mod})")
            case "buff":
                buff_stat = effect["stat"]
                buff_by = effect["value"]
                duration = effect["duration"]
                if does_crit:
                    buff_by *= 2
                target_stat_current = getattr(target, buff_stat)
                buffed_total = target_stat_current + buff_by
                setattr(target, buff_stat, buffed_total)
                upper_buff_stat = buff_stat.upper()
                log_event(f"{target.name} has had their {upper_buff_stat} increased by {buff_by}({target_stat_current}->{getattr(target, buff_stat)})")
                buff_info = {
                    "stat": buff_stat,
                    "value": buff_by,
                    "duration_left": duration,
                    "id": str(uuid.uuid4()) #unique identifiers for removal
                }
                target.buffs.append(buff_info)
            case "spell_buff":
                handle_spell_slots(effect, user)
                buff_stat = effect["stat"]
                buff_by = effect["value"]
                duration = effect["duration"]
                if does_crit:
                    buff_by *= 2
                target_stat_current = getattr(target, buff_stat)
                buffed_total = target_stat_current + buff_by
                setattr(target, buff_stat, buffed_total)
                upper_buff_stat = buff_stat.upper()
                log_event(f"{target.name} has had their {upper_buff_stat} increased by {buff_by}({target_stat_current}->{getattr(target, buff_stat)})")
                buff_info = {
                    "stat": buff_stat,
                    "value": buff_by,
                    "duration_left": duration,
                    "id": str(uuid.uuid4())
                }
                target.buffs.append(buff_info)
            case "debuff":
                debuff_stat = effect["stat"]
                debuff_by = effect["value"]
                duration = effect["duration"]
                if does_crit:
                    debuff_by *= 2
                target_stat_current = getattr(target, debuff_stat)
                debuffed_total = target_stat_current - debuff_by
                setattr(target, debuff_stat, debuffed_total)
                upper_debuff_stat = debuff_stat.upper()
                log_event(f"{target.name} has had their {upper_debuff_stat} decreased by {debuff_by}({target_stat_current}->{getattr(target, debuff_stat)})")
                debuff_info = {
                    "stat": debuff_stat,
                    "value": debuff_by,
                    "duration_left": duration,
                    "id": str(uuid.uuid4())
                }
                target.debuffs.append(debuff_info)
            case "spell_debuff":
                handle_spell_slots(effect, user)
                debuff_stat = effect["stat"]
                debuff_by = effect["value"]
                duration = effect["duration"]
                if does_crit:
                    debuff_by *= 2
                target_stat_current = getattr(target, debuff_stat)
                debuffed_total = target_stat_current - debuff_by
                setattr(target, debuff_stat, debuffed_total)
                upper_debuff_stat = debuff_stat.upper()
                log_event(f"{target.name} has had their {upper_debuff_stat} decreased by {debuff_by}({target_stat_current}->{getattr(target, debuff_stat)})")
                debuff_info = {
                    "stat": debuff_stat,
                    "value": debuff_by,
                    "duration_left": duration,
                    "id": str(uuid.uuid4())
                }
                target.debuffs.append(debuff_info)
    
def handle_rest_per_use(ability, player):
    if ability["uses_per_rest"] > 0:
        if ability["name"] not in player.rest_usage:
            player.rest_usage[ability["name"]] = 1
        else:
            player.rest_usage[ability["name"]] += 1

def handle_spell_slots(effect, player):
    if effect["spell_slot_level"] > 0:
        player.spell_slots[str(effect["spell_slot_level"])] -= 1

def attack_roll(ability_user, target, ability_name):
    does_crit = False
    for ability in ability_user.abilities:
        if ability["name"] == ability_name:
            ability_info = ability
            ability_stat = ability["modifier_stat"]
    stat_mod = find_stat_mod(ability_user, ability_stat)
    roll, roll_list = dice_roller(20, 1, stat_mod) # attack rolls will not have advantage/disadvantage support in MVP. dis/advantage will mostly be for skill checks in the story
    log_event(f"Attack rolled: {roll}({roll_list}+{stat_mod})")
    if roll - stat_mod >= 20: # doing subtraction here to get the raw roll, instead of trying to pull the roll list through. may change later.
        does_crit = True
    if roll >= target.ac or does_crit:
        return True, does_crit
    else:
        return False, False
       
def find_stat_mod(character, ability_stat):
    stat_mod = 0
    if ability_stat == "physical":
        str_mod = character.get_modifier(character.strength)
        dex_mod = character.get_modifier(character.dex)
        stat_mod = max(str_mod, dex_mod)
    else:
        stat_mod = character.get_modifier(getattr(character, ability_stat, 10)) #defaults to 10 if there's a weird stat mod.
    return stat_mod

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

player = Player(1, 10, 16, 16, 12, 10, 8, 8, 15, "AggroSec", "2d6", {"1": 1}, "Greataxe", ["swing", "chop", "cleave"])
new_ability = {
  "name": "Smite Evil",
  "description": "Strike with holy power, harming and weakening undead",
  "uses_per_rest": 0,
  "modifier_stat": "wis",
  "attack_descs": [
    "You pray to the heavens, and as you strike a holy bolt from the sky flies with you, smiting (t)"
  ],
  "attack_misses": [
    "You pray for smiting power, but there is no answer... Silence fills the void."
  ],
  "effects": [
    {
      "type": "spell_damage",
      "value": "8",
      "spell_slot_level": 1,
      "target": "enemy",
      "extra": {"damage_type": "radiant"}
    },
    {
      "type": "spell_debuff",
      "stat": "strength",
      "value": 2,
      "duration": 2,
      "spell_slot_level": 0,
      "target": "enemy"
    }
  ]
}
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
        "value": "2d12",
        "target": "enemy"
        }
    ]
    }
)
player.add_ability(
    {
    "name": "Derp Heal",
    "description": "During travels doing trades, you have learned to sing a healing song of magic",
    "uses_per_rest": 3,
    "modifier_stat": "wis",
    "attack_descs": [
        "Singing out in a loud voice, (a) enunciates, 'glory be, look at me, heal me with sing'"
    ],
    "attack_misses": [
        "N/A"
    ],
    "effects": [
        {
        "type": "heal",
        "value": "1d4",
        "target": "ally"
        }
    ]
    }
)
player.add_ability(
    {
    "name": "Singing Heal",
    "description": "During travels doing trades, you have learned to sing a healing song of magic",
    "uses_per_rest": 2,
    "modifier_stat": "wis",
    "attack_descs": [
        "Singing out in a loud voice, (a) enunciates, 'glory be, look at me, heal me with sing'"
    ],
    "attack_misses": [
        "N/A"
    ],
    "effects": [
        {
        "type": "heal",
        "value": "1d8",
        "target": "ally"
        },
        {
            "type": "spell_buff",
            "stat": "wis",
            "value": 2,
            "duration": 3,
            "spell_slot_level": 1,
            "target": "ally"
        }
    ]
    }
)
player.add_ability(new_ability)
enemy1 = EnemyNPC(1,20,1,10,10,1,1,1,10,"Bob the minion","1d2",10)
enemy2 = EnemyNPC(1,1,1,1,10,1,1,1,20,"Bob the chieftain","1d6",50)
handle_player_turn(player, [enemy1, enemy2])