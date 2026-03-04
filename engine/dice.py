import random

def dice_roller(sides, dice = 1, modifier = 0, advantage = False, disadvantage = False):
    if (dice > 1 and (advantage or disadvantage)):
        raise ValueError("advantage on multiple rolls is not supported")
    if (dice < 1):
        raise ValueError("can't roll less than 1 die")
    die_roll = 0
    roll_list = []
    if dice > 1:
        die_roll, roll_list = handle_multi_total(sides, dice)
    elif advantage and not disadvantage:
        die_roll, roll_list = handle_comparison_dice(sides, True, False)
    elif disadvantage and not advantage:
        die_roll, roll_list = handle_comparison_dice(sides, False, True)
    elif advantage and disadvantage:
        print("how unlucky, your advantage was cancelled out")
        die_roll = random.randint(1, sides)
        roll_list.append(die_roll)
    elif not advantage and not disadvantage:
        die_roll = random.randint(1, sides)
        roll_list.append(die_roll)
    die_roll += modifier
    return (die_roll, roll_list)

def handle_multi_total(sides, dice):
    total = 0
    roll_list = []
    for i in range(dice):
        roll, _ = dice_roller(sides)
        roll_list.append(roll)
        total += roll
    return (total, roll_list)

def handle_comparison_dice(sides, advantage, disadvantage):
    roll_list = []
    roll1, _ = dice_roller(sides)
    roll2, _ = dice_roller(sides)
    roll_list.append(roll1)
    roll_list.append(roll2)
    if advantage:
        return (max(roll1, roll2), roll_list)
    elif disadvantage:
        return (min(roll1, roll2), roll_list)
    else:
        raise ValueError("can't have both advantage and disadvantage")