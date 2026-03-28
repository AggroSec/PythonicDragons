from engine.character import *
from engine.choice import *
from engine.dice import *
from engine.combat import *
from pathlib import Path
from tabulate import tabulate
import json
import time

def start_game():
    player = character_creation()



def character_creation():
    name = get_name()
    player_class = get_class()
    log_game_event(f"Welcome, {name} the {player_class['name']}! Your adventure begins now.")
    

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

def log_game_event(text):
    print(text)

def generic_get_input(prompt):
    return input(prompt)
