from engine.character import *
from engine.choice import *
from engine.dice import *
from engine.combat import *
from pathlib import Path
from tabulate import tabulate
import json
import time

def start_game():
    player, class_info = character_creation()
    story = get_story_selection()
    game_finished = False
    current_scene = story['start_scene']
    while not game_finished:
        current_scene, game_finished = handle_scenes(player, story, current_scene, class_info)

def handle_scenes(player, story, current_scene, class_info):
    scene_data = story['scenes'][current_scene]
    if scene_data["game_finished"] == True:
        log_game_event(scene_data["text"])
        return current_scene, True
    elif scene_data["combat"] == True:
        log_game_event(scene_data["text"])
        enemies_list = load_json_data("data/enemies.json")
        combat_enemies = []
        for enemy_name in scene_data["combat_info"]["enemies"]:
            for enemy in enemies_list:
                if enemy["name"] == enemy_name:
                    created_enemy = EnemyNPC(
                        1, 
                        enemy["hp"], 
                        enemy["constitution"], 
                        enemy["strength"], 
                        enemy["dexterity"], 
                        enemy["intelligence"], 
                        enemy["wisdom"], 
                        enemy["ris"], 
                        enemy["ac"], 
                        enemy["name"], 
                        enemy["basic_attack"]["value"], 
                        enemy["ability_probability"], 
                        enemy["basic_attack"]["name"], 
                        enemy["basic_attack"]["verb"]
                    )
                    for ability in enemy.get("abilities", []):
                        created_enemy.add_ability(ability)
                    combat_enemies.append(created_enemy)
        combat_success = run_combat(player, combat_enemies)
        if combat_success:
            log_game_event("You have survived to see another day...")
            return scene_data["combat_info"]["win"], False
        else:
            log_game_event("You have been defeated...")
            return scene_data["combat_info"]["lose"], False
    elif scene_data["rest"] == True:
        player.spell_slots = class_info["spell_slots"]
        player.current_hp = player.max_hp
        player.rest_usage = {}
        next_scene = present_scene(scene_data, player)
        log_game_event("You have rested and recovered your health and spell slots.")
        return next_scene, False
    else:
        next_scene = present_scene(scene_data, player)
        return next_scene, False
        

def character_creation():
    while True:
        name = get_name()
        player_class = get_class()
        log_game_event(f"Welcome, {name} the {player_class['name']}! Your adventure begins begins shortly.")
        weapon_info = get_weapon_selection(player_class)
        stats = get_stat_allocation()
        display_character_sheet(name, player_class, stats, weapon_info)
        finished = get_confirmation()
        if finished:
            log_game_event("Character creation complete! Starting game...")
            created_character = initialize_character(name, player_class, stats, weapon_info)
            time.sleep(1)
            return created_character, player_class
        else:
            log_game_event("Reallocating stats. Returning to stat allocation screen...")
            time.sleep(1)
    
    

def load_json_data(file_path: str):
    '''generic function to take json file and load into a variable.
    should work on any json file, just pass the path.'''
    
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

def get_name():
    log_game_event("What name do you wish to be known by?")
    while True:
        name_input = generic_get_input("Enter your name: ").strip()
        if type(name_input) != str or len(name_input) == 0:
            log_game_event("Invalid name, try again.")
        elif len(name_input) > 20:
            log_game_event("Name too long, try again.")
        else:
            return name_input
        
def get_class():
    selectable_classes = load_json_data("data/classes.json")
    log_game_event("What has been your chosen path? (class selection)")
    for index in range(len(selectable_classes)):
        class_name = selectable_classes[index]['name']
        log_game_event(f"{index+1}. {class_name}")
    while True:
        class_input = generic_get_input("Enter the number corresponding to your chosen class (or info [number] for more info on the class): ").strip()
        if not class_input.isdigit():
            if "info" in class_input.lower():
                info_parts = class_input.lower().split()
                if len(info_parts) == 2 and info_parts[0] == "info" and info_parts[1].isdigit():
                    info_index = int(info_parts[1]) - 1
                    if 0 <= info_index < len(selectable_classes):
                        class_info = selectable_classes[info_index]
                        show_class_info(class_info)
                        continue
                    else:
                        log_game_event("Invalid class number for info, try again.")
                        continue
                else:
                    log_game_event("Invalid input format for info, try again.")
                    continue
            else:
                log_game_event("Invalid input, please enter a number.")
                continue
        class_index = int(class_input) - 1
        if class_index < 0 or class_index >= len(selectable_classes):
            log_game_event("Invalid selection, try again.")
            continue
        return selectable_classes[class_index]
    
def get_weapon_selection(player_class):
    weapon_options = player_class.get('weapons', [])
    if not weapon_options:
        log_game_event("No starting weapons available for this class.")
        return None
    log_game_event("Select your starting weapon:")
    table = []
    for i, weapon in enumerate(weapon_options, 1):
        table.append([
            i,
            weapon["name"].capitalize(),
            weapon["attack_string"]
        ])
    
    log_game_event(tabulate(table, headers=["#", "Weapon", "Damage"], tablefmt="grid"))
    log_game_event("")
    while True:
        weapon_input = generic_get_input("Enter the number corresponding to your chosen weapon: ").strip()
        if not weapon_input.isdigit():
            log_game_event("Invalid input, please enter a number.")
            continue
        weapon_index = int(weapon_input) - 1
        if weapon_index < 0 or weapon_index >= len(weapon_options):
            log_game_event("Invalid selection, try again.")
            continue
        return weapon_options[weapon_index]
    
def show_class_info(class_info):
    """Display detailed information about a class using tabulate and log_game_event"""
    
    log_game_event(f"\n=== {class_info['name']} ===\n")
    log_game_event(class_info['description'])
    log_game_event("-" * 50)

    # Basic Stats Table
    stats_data = [
        ["Hit Die", f"d{class_info['hit_die']}"],
        ["Base AC", class_info.get('base_ac', 'N/A')],
        ["Strength", f"+{class_info['stat_modifiers'].get('strength', 0)}"],
        ["Dexterity", f"+{class_info['stat_modifiers'].get('dex', 0)}"],
        ["Constitution", f"+{class_info['stat_modifiers'].get('con', 0)}"],
        ["Intelligence", f"+{class_info['stat_modifiers'].get('intel', 0)}"],
        ["Wisdom", f"+{class_info['stat_modifiers'].get('wis', 0)}"],
        ["Charisma", f"+{class_info['stat_modifiers'].get('ris', 0)}"]
    ]

    stats_table = tabulate(stats_data, headers=["Stat", "Value"], tablefmt="grid")
    log_game_event(stats_table)
    log_game_event("")

    # Abilities List
    if class_info.get('abilities'):
        log_game_event("Abilities:")
        ability_list = []
        for ability in class_info['abilities']:
            ability_list.append([ability['name'], ability.get('description', '')])
        
        abilities_table = tabulate(ability_list, headers=["Ability", "Description"], tablefmt="grid")
        log_game_event(abilities_table)
    
    log_game_event("")

def get_stat_allocation():
    strength = 8
    constitution = 8
    dexterity = 8
    intelligence = 8
    wisdom = 8
    charisma = 8
    points = 27
    stat_cost_dict = {
        8: 0,
        9: 1,
        10: 2,
        11: 3,
        12: 4,
        13: 5,
        14: 7,
        15: 9
    }
    log_game_event("You have 27 points to allocate to your stats. Each stat starts at 8 and can be increased up to 15. The cost to increase stats is as follows:")
    show_cost()
    while points > 0:
        log_game_event(f"You have {points} points remaining.")
        show_stat_allocation(strength, constitution, dexterity, intelligence, wisdom, charisma)
        log_game_event("To allocate points, enter the stat name followed by the desired value (e.g. 'strength 14').")
        log_game_event("It is recommended to allocate points in order of importance for your chosen class. When you are finished allocating points, enter 'done'.")
        stat_input = generic_get_input("Enter the stat you want to increase (or 'done' to finish): ").strip().lower()
        if stat_input == "done":
            break
        split_input = stat_input.split(" ")
        if len(split_input) != 2 or not split_input[1].isdigit():
            log_game_event("Invalid input format, try again.")
            continue
        stat_name = split_input[0]
        stat_assignment = int(split_input[1])
        log_game_event(f"Attempting to assign {stat_assignment} to {stat_name}.")
        if stat_assignment < 8 or stat_assignment > 15:
            log_game_event("Stat value must be between 8 and 15, try again.")
            continue
        if stat_name == "strength":
            if strength > 8:
                log_game_event("Stat has already been assigned, try again.")
                continue
            else:
                cost = stat_cost_dict[stat_assignment]
                if cost > points:
                    log_game_event("Not enough points for that assignment, try again.")
                    continue
                strength = stat_assignment
                points -= cost
        elif stat_name == "constitution":
            if constitution > 8:
                log_game_event("Stat has already been assigned, try again.")
                continue
            else:
                cost = stat_cost_dict[stat_assignment]
                if cost > points:
                    log_game_event("Not enough points for that assignment, try again.")
                    continue
                constitution = stat_assignment
                points -= cost
        elif stat_name == "dexterity":
            if dexterity > 8:
                log_game_event("Stat has already been assigned, try again.")
                continue
            else:
                cost = stat_cost_dict[stat_assignment]
                if cost > points:
                    log_game_event("Not enough points for that assignment, try again.")
                    continue
                dexterity = stat_assignment
                points -= cost
        elif stat_name == "intelligence":
            if intelligence > 8:
                log_game_event("Stat has already been assigned, try again.")
                continue
            else:
                cost = stat_cost_dict[stat_assignment]
                if cost > points:
                    log_game_event("Not enough points for that assignment, try again.")
                    continue
                intelligence = stat_assignment
                points -= cost
        elif stat_name == "wisdom":
            if wisdom > 8:
                log_game_event("Stat has already been assigned, try again.")
                continue
            else:
                cost = stat_cost_dict[stat_assignment]
                if cost > points:
                    log_game_event("Not enough points for that assignment, try again.")
                    continue
                wisdom = stat_assignment
                points -= cost
        elif stat_name == "charisma":
            if charisma > 8:
                log_game_event("Stat has already been assigned, try again.")
                continue
            else:
                cost = stat_cost_dict[stat_assignment]
                if cost > points:
                    log_game_event("Not enough points for that assignment, try again.")
                    continue
                charisma = stat_assignment
                points -= cost
        else:
            log_game_event("Invalid stat name, try again.")
            continue
    return {"strength": strength, "con": constitution, "dex": dexterity, "intel": intelligence, "wis": wisdom, "ris": charisma}

def show_cost():
    cost_table = [
        [8, 0],
        [9, 1],
        [10, 2],
        [11, 3],
        [12, 4],
        [13, 5],
        [14, 7],
        [15, 9]
    ]
    display_table = tabulate(cost_table, headers=["Stat Value", "Cost"], tablefmt="grid")
    log_game_event(display_table)
    
def show_stat_allocation(strength, constitution, dexterity, intelligence, wisdom, charisma):
    stat_table = [
        ["Strength", strength],
        ["Constitution", constitution],
        ["Dexterity", dexterity],
        ["Intelligence", intelligence],
        ["Wisdom", wisdom],
        ["Charisma", charisma]
    ]
    display_table = tabulate(stat_table, headers=["Stat", "Value"], tablefmt="grid")
    log_game_event(display_table)

def display_character_sheet(name, player_class, stats, weapon_info):
    log_game_event(f"\n=== Character Sheet for {name} the {player_class['name']} ===\n")
    log_game_event(f"Class: {player_class['name']}")
    log_game_event(f"Description: {player_class['description']}")
    log_game_event("-" * 50)

    dex_mod = calculate_dex_mod(stats, player_class)

    # Basic Stats Table
    stats_data = [
        ["Hit Die", f"d{player_class['hit_die']}"],
        ["Base AC (plus dex modifier)", f"{player_class.get('base_ac', 'N/A')}+{dex_mod}"],
        ["Strength", f"{stats['strength']}+{player_class['stat_modifiers'].get('strength', 0)}"],
        ["Dexterity", f"{stats['dex']}+{player_class['stat_modifiers'].get('dex', 0)}"],
        ["Constitution", f"{stats['con']}+{player_class['stat_modifiers'].get('con', 0)}"],
        ["Intelligence", f"{stats['intel']}+{player_class['stat_modifiers'].get('intel', 0)}"],
        ["Wisdom", f"{stats['wis']}+{player_class['stat_modifiers'].get('wis', 0)}"],
        ["Charisma", f"{stats['ris']}+{player_class['stat_modifiers'].get('ris', 0)}"]
    ]

    stats_table = tabulate(stats_data, headers=["Stat", "Value"], tablefmt="grid")
    log_game_event(stats_table)
    log_game_event("")
    log_game_event(f"Selected Weapon: {weapon_info['name'].capitalize()} (Damage: {weapon_info['attack_string']})")
    log_game_event("")

     # Abilities List
    if player_class.get('abilities'):
        log_game_event("Abilities:")
        ability_list = []
        for ability in player_class['abilities']:
            ability_list.append([ability['name'], ability.get('description', '')])
        
        abilities_table = tabulate(ability_list, headers=["Ability", "Description"], tablefmt="grid")
        log_game_event(abilities_table)
    log_game_event("")

def calculate_dex_mod(stats, player_class):
    base_dex = stats['dex']
    class_dex_mod = player_class['stat_modifiers'].get('dex', 0)
    total_dex = base_dex + class_dex_mod
    dex_mod = (total_dex - 10) // 2
    return dex_mod

def get_confirmation():
    log_game_event("Are you satisfied with your character sheet? (yes/no)")
    while True:
        confirmation_input = generic_get_input("Enter 'yes' to confirm or 'no' to reallocate stats: ").strip().lower()
        if confirmation_input == "yes":
            return True
        elif confirmation_input == "no":
            return False
        else:
            log_game_event("Invalid input, please enter 'yes' or 'no'.")

def initialize_character(name, player_class, stats, weapon_info):
    hit_die = player_class['hit_die']
    base_ac = player_class.get('base_ac', 10) + calculate_dex_mod(stats, player_class)
    strength = stats['strength'] + player_class['stat_modifiers'].get('strength', 0)
    dexterity = stats['dex'] + player_class['stat_modifiers'].get('dex', 0)
    constitution = stats['con'] + player_class['stat_modifiers'].get('con', 0)
    intelligence = stats['intel'] + player_class['stat_modifiers'].get('intel', 0)
    wisdom = stats['wis'] + player_class['stat_modifiers'].get('wis', 0)
    charisma = stats['ris'] + player_class['stat_modifiers'].get('ris', 0)
    abilities = player_class.get('abilities', [])
    character = Player(
        1, 
        hit_die, 
        constitution, 
        strength, 
        dexterity,
        intelligence,
        wisdom,
        charisma,
        base_ac,
        name,
        weapon_info["attack_string"],
        player_class["spell_slots"],
        weapon_info["name"],
        weapon_info["weapon_verb"]
        )
    for ability in player_class.get('abilities', []):
        character.add_ability(ability)
    return character

def get_story_selection():
    """
    Scans the stories/ folder and returns a list of story names (folder names)
    and their full paths to story.json
    """
    stories_dir = Path("stories")
    
    if not stories_dir.exists():
        raise FileNotFoundError(f"Stories directory not found: {stories_dir}")
    
    story_list = []
    
    # Iterate through each subfolder in stories/
    for story_folder in stories_dir.iterdir():
        if story_folder.is_dir():
            story_file = story_folder / "story.json"
            if story_file.exists():
                story_list.append({
                    "name": story_folder.name,           # e.g. "default", "lost_caravan"
                    "path": str(story_file),             # full relative path
                    "display_name": story_folder.name.replace("_", " ").title()
                })
    
    # Sort alphabetically for nice display
    story_list.sort(key=lambda x: x["display_name"])
    log_game_event("Available Stories:")
    for index, story in enumerate(story_list, 1):
        log_game_event(f"{index}. {story['display_name']} - {story['path']}")
    player_input = generic_get_input("Enter the number corresponding to the story you want to play: ").strip()
    while True:
        if not player_input.isdigit():
            log_game_event("Invalid input, please enter a number.")
            player_input = generic_get_input("Enter the number corresponding to the story you want to play: ").strip()
            continue
        story_index = int(player_input) - 1
        if story_index < 0 or story_index >= len(story_list):
            log_game_event("Invalid selection, try again.")
            player_input = generic_get_input("Enter the number corresponding to the story you want to play: ").strip()
            continue
        chosen_story_path = story_list[story_index]["path"]
        log_game_event(f"You have selected: {story_list[story_index]['display_name']}")
        return load_json_data(chosen_story_path)

def log_game_event(text):
    print(text)

def generic_get_input(prompt):
    return input(prompt)
