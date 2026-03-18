from engine.character import *
from engine.dice import *
from engine.combat import *
def main():
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
    enemy1 = EnemyNPC(1,20,1,10,10,1,1,1,5,"Bob the minion","1d2",0)
    enemy2 = EnemyNPC(1,1,1,1,8,1,1,1,10,"Bob the chieftain","1d6",50)
    enemy2.add_ability(
        {
        "name": "Power Swing",
        "description": "During travels doing trades, you have learned to put some oomph in your weapon attacks",
        "uses_per_rest": 0,
        "modifier_stat": "physical",
        "attack_descs": [
            "Singing out in a loud voice, (a) enunciates, 'glory be, look at me, put some OOMPH in this swing' as he swings his weapon at you."
        ],
        "attack_misses": [
            "(a) begins to sing as he swings his weapon, but falters, losing the rythm. The attack goes wide, missing you completely"
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
    enemy2.add_ability(
        {
        "name": "Singing Heal",
        "description": "During travels doing trades, you have learned to sing a healing song of magic",
        "uses_per_rest": 0,
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
                "stat": "dex",
                "value": 2,
                "duration": 3,
                "spell_slot_level": 0,
                "target": "ally"
            }
        ]
        }
    )
    run_combat(player, [enemy1,enemy2])


if __name__ == "__main__":
    main()
