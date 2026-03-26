from engine.dice import *
from engine.character import *
import time

def present_scene(scene_dict: dict, player: Player): # may add checks against enemies later, not for MVP
    choices = []
    story_text = scene_dict["text"]
    log_story_event(story_text)
    if scene_dict["check"] == True:
        check_info = scene_dict["check_info"]
        stat = check_info["stat"]
        dc = check_info["dc"]
        advantage = check_info["advantage"]
        disadvantage = check_info["disadvantage"]
        success = skill_check(player, stat, dc, advantage, disadvantage)
        if success:
            time.sleep(1)
            return check_info["success"]
        else:
            time.sleep(1)
            return check_info["failure"]
    for choice in scene_dict["choices"]:
        choices.append(choice["text"])
    chosen_index = player_story_choice(choices, player)
    choice_dict = scene_dict["choices"]
    return choice_dict[chosen_index]["next"]

def player_story_choice(choices, player):
    log_story_event(f"what do you choose to do, {player.name}? (num)")
    for i, opt in enumerate(choices, 1):
        log_story_event(f"[{i}] {opt}")
    while True:
        try:
            player_input = input("[STORY]: ").strip().lower()
            if int(player_input) >= 1 and int(player_input) <= len(choices):
                return int(player_input) - 1
            else:
                raise ValueError
        except ValueError:
            log_story_event("Invalid choice, try again.")


def skill_check(player, stat: str, DC: int, advantage=False, disadvantage=False):
    stat_mod = player.get_modifier(getattr(player, stat, 10)) # same thing as in combat, defaults to 10
    upper_stat = stat.upper()
    check_roll, rolls = dice_roller(20, 1, stat_mod, advantage, disadvantage)
    log_story_event(f"SKILL CHECK[{upper_stat}]: you rolled a {check_roll}({rolls}+{stat_mod})")
    if check_roll >= DC:
        log_story_event("Check successful!")
        return True
    else:
        log_story_event("Check failed...")
        return False


def log_story_event(text):
    print(text)

