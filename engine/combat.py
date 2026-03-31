from engine.dice import *
from engine.character import *
from tabulate import tabulate
import random, uuid, time

def run_combat(player, enemies=[]):
    '''
    TLDR: no bonus actions at this point.

    Some caveats for the MVP code, and it will be stated in the readme, this is not a 1 to 1 translation of DnD rules, just heavily inspired by it.
    If this project takes off, people want things added, I come back to improve when I have more time I'll add things like bonus actions. For now to keep
    it simple this is one of the few things that will be left out/changed from actual DnD rules
    '''
    turn_break = "◆──────────────────────────────────────────────◆"
    round_break = "᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛᚛"
    log_event("======Combat has been initiated!======")
    time.sleep(0.5)
    initiative = roll_initiative(player, enemies)
    turn_order = get_turn_order(initiative)
    current_round = 1
    log_event(f"Initiatives have been determined: {turn_order}")
    game_over = False
    while not game_over:
        log_event(round_break)
        log_event(f"Round {current_round} start")
        log_event(round_break)
        for name in turn_order:
            if name == player.name:
                log_event(turn_break)
                log_event(f"{player.name}'s turn")
                log_event(turn_break)
                time.sleep(0.5)
                handle_player_turn(player, enemies)
                time.sleep(2.0)
            else:
                for enemy in enemies:
                    if name == enemy.name:
                        log_event(turn_break)
                        log_event(f"{enemy.name}'s turn")
                        log_event(turn_break)
                        time.sleep(0.5)
                        handle_enemy_turn(enemy, player)
                        time.sleep(1.0)
                        status_update(enemy, player)
                        time.sleep(2.0)
        turn_order, game_over = round_clean_up(player, enemies, initiative)
        time.sleep(1.0)
        log_event(round_break)
        log_event(f"Round {current_round} END")
        log_event(round_break)
        time.sleep(0.5)
        player_info_prompt(player)
        time.sleep(2.0)
        current_round += 1
    if player.current_hp > 0:
        player.buffs = []
        player.debuffs = []
        return True
    else:
        return False

def player_info_prompt(player):
    buffs = ""
    debuffs = ""
    for buff in player.buffs:
        stat = buff["stat"]
        value = buff["value"]
        duration = buff["duration_left"]
        buffs += f"<{stat}|V:{value}|D:{duration}>"
    for debuff in player.debuffs:
        stat = debuff["stat"]
        value = debuff["value"]
        duration = debuff["duration_left"]
        debuffs += f">{stat}|V:{value}|D:{duration}<"
    prompt_string = f"Status(Name: {player.name} | Health: {player.current_hp}/{player.max_hp} | USAGE: {player.rest_usage} | SPELL SLOTS: {player.spell_slots} | BUFFS: {buffs} | DEBUFFS: {debuffs})"
    log_event(prompt_string)

def round_clean_up(player, enemies, initiative_dict):
    game_over = False
    if player.current_hp <= 0:
        game_over = True
    all_enemies_dead = True
    for enemy in enemies:
        if enemy.current_hp > 0:
            all_enemies_dead = False
    if all_enemies_dead:
        game_over = True
    if game_over:
        return [], game_over
    
    handle_buffs_and_debuffs(player)
    dead_enemies = []
    for enemy in enemies:
        if enemy.current_hp > 0:
            handle_buffs_and_debuffs(enemy)
        else:
            dead_enemies.append(enemy.name)
    
    for dead_enemy in dead_enemies:
        if dead_enemy in initiative_dict:
            del initiative_dict[dead_enemy]
    
    new_turn_order = get_turn_order(initiative_dict)

    return new_turn_order, game_over
    

def handle_buffs_and_debuffs(character):
    removal_buffs = []
    removal_debuffs = []

    for buff in character.buffs:
        unique_id = buff["id"]
        if buff["duration_left"] <= 0:
            removal_buffs.append(unique_id)
        else:
            buff["duration_left"] -= 1
    
    for debuff in character.debuffs:
        unique_id = debuff["id"]
        if debuff["duration_left"] <= 0:
            removal_debuffs.append(unique_id)
        else:
            debuff["duration_left"] -= 1

    for unique_id in removal_buffs:
        for buff in character.buffs:
            if buff["id"] == unique_id:
                stat = buff["stat"]
                value = buff["value"]
                current_stat = getattr(character, stat)
                new_stat = current_stat - value
                setattr(character, stat, new_stat)
                log_event(f"{character.name}'s {stat} buff has expired.(-{value})")

    for unique_id in removal_debuffs:
        for debuff in character.debuffs:
            if debuff["id"] == unique_id:
                stat = debuff["stat"]
                value = debuff["value"]
                current_stat = getattr(character, stat)
                new_stat = current_stat + value
                setattr(character, stat, new_stat)
                log_event(f"{character.name}'s {stat} debuff has expired.(+{value})")

    character.buffs = [b for b in character.buffs if b["id"] not in removal_buffs]
    character.debuffs = [d for d in character.debuffs if d["id"] not in removal_debuffs]

def handle_enemy_turn(enemy, player):
    if enemy.current_hp <= 0:
        log_event(f"{enemy.name} is dead, no longer a threat to you.")
        return
    ability_roll = random.randint(1, 100)
    if ability_roll <= enemy.ability_use_chance:
        handle_enemy_abilities(enemy, player)
    else:
        enemy_basic_attack(enemy, player)

def handle_enemy_abilities(enemy, player):
    if not enemy.abilities:
        log_event("WARNING: Enemy does not have abilities, but chance level was provided, check json data. Running basic attack")
        enemy_basic_attack(enemy, player)
        return
    chosen_ability = random.choice(enemy.abilities)
    if chosen_ability["effects"][0]["target"] == "ally":
        target = enemy
    else:
        target = player
    use_ability(enemy, target, chosen_ability["name"])

def enemy_basic_attack(enemy, player):
    stat_mod = find_stat_mod(enemy, "physical")
    does_hit, does_crit = attack_roll(enemy, player, "", False, stat_mod)
    if does_hit or does_crit:
        die_num = enemy.basic_attack["num_die"]
        sides = enemy.basic_attack["sides"]
        damage, rolls = dice_roller(sides, die_num, stat_mod)
        if does_crit:
            damage *= 2
            log_event(f"{enemy.name} scores a CRIT!")
        player.damage_hp(damage)
        weapon = enemy.weapon
        verb = random.choice(enemy.weapon_verb)
        if damage >= 30:
            blow_string = "~*cataclysmic*~ strike of pure ruin on you."
        elif damage >= 20:
            blow_string = "~-earth-shattering*~ blow on you."
        elif damage >= 15:
            blow_string = "-devastating- blow, staggering you."
        elif damage >= 10:
            blow_string = "hefty blow, driving you back, causing moderate bleeding."
        elif damage >= 5:
            blow_string = "solid blow, opening minor wounds on you."
        elif damage >= 1:
            blow_string = "glancing blow, barely causing a scratch."
        else:
            blow_string = "frail blow, bouncing off you harmlessly."
        attack_desc = f"{enemy.name} {verb} their {weapon} at you, landing a {blow_string} ({damage}[{rolls}+{stat_mod}])"
        log_event(attack_desc)
    else:
        miss_strings = [
            f"{enemy.name} moves to attack you, you dodge to the side, the attack wiffing air.",
            f"{enemy.name} tries to hit you, the blow glances off your armor."
        ]
        miss_string = random.choice(miss_strings)
        log_event(miss_string)

def handle_player_turn(player, enemies):
    choices = [ability["name"] for ability in player.abilities]
    action = player_choice("It's your move, what do you choose(number|info [num]|status)?", choices, player)
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
        enemy_list = [enemy.name for enemy in enemies if enemy.current_hp > 0]
        enemy_name = player_choice("Who are you targeting(number)?", enemy_list, targeter, selecting_target=True)
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
    time.sleep(0.5)
    log_event(f"{player.name} rolled a {player_initiative}({actual_roll}+{player.get_modifier(player.dex)})")
    for enemy in enemies:
        initiative_roll, actual_roll = dice_roller(20, 1, enemy.get_modifier(enemy.dex))
        initiative_rolls[enemy.name] = initiative_roll
        time.sleep(0.5)
        log_event(f"{enemy.name} rolled a {initiative_roll}({actual_roll}+{enemy.get_modifier(enemy.dex)})")
    return initiative_rolls


def log_event(message):
    '''currently just prints to console, can be extended to work with GUI or TUI (hopefully) without effecting combat logic'''
    print(message)

def player_choice(prompt, choices=[], player=None, selecting_target=False):
    '''again thinking of future extensiblity, for now takes what the caller wants to prompt the user, and valid choices,
    and validates the player choice before returning the choice. if not valid, prompts to pick again until a valid choice is given'''
    log_event(prompt)
    for i, opt in enumerate(choices, 1):
        log_event(f"[{i}] {opt}")
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
            if "status" in choice:
                player_info_prompt(player)
                continue
            if 1 <= int(choice) <= len(choices):
                if selecting_target:
                    return choices[int(choice)-1]
                elif can_use_ability(player, choices[int(choice)-1]):
                    return choices[int(choice)-1]
                else:
                    raise ValueError
            else:
                log_event(f"Choice must be between 1 and {len(choices)}")
        except ValueError:
            log_event("Invalid choice, try again!")

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
        hit_line = hit_line.replace("(v)", random.choice(ability_user.weapon_verb)).replace("(a)", ability_user.name).replace("(t)", target.name).replace("(w)", ability_user.weapon)
        damage_art_left = "───═( "
        damage_art_right = " )═───"
        log_event(f"{damage_art_left}{hit_line}{damage_art_right}")
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

def attack_roll(ability_user, target, ability_name="", get_stat=True, passed_mod=0):
    does_crit = False
    if ability_name != "":
        for ability in ability_user.abilities:
            if ability["name"] == ability_name:
                ability_info = ability
                ability_stat = ability["modifier_stat"]
    if get_stat:
        stat_mod = find_stat_mod(ability_user, ability_stat)
    else:
        stat_mod = passed_mod
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


