class Character:

    def __init__(self, level, max_hp, con=8, strength=8, dex=8, intel=8, wis=8, ris=8, ac=10, base_attack="1d6"):
        self.level = level
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.con = con
        self.strength = strength
        self.dex = dex
        self.intel = intel
        self.wis = wis
        self.ris = ris
        self.ac = self.get_ac(ac)
        self.abilities = []
        self.basic_attack = self.set_basic_attack(base_attack)
        
    def get_modifier(self, stat):
        return (stat - 10) // 2
    
    def get_ac(self, base):
        return base + self.get_modifier(self.dex)
    
    def heal_hp(self, amount):
        if amount < 0:
            raise ValueError("what is this sorcery called 'negative numbers'")
        self.current_hp += amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp

    def damage_hp(self, amount):
        if amount < 0:
            raise ValueError("what is this sorcery called 'negative numbers'")
        self.current_hp -= amount
        if self.current_hp < 0:
            self.current_hp = 0
    
    def add_ability(self, ability):
        self.abilities.append(ability)

    def set_basic_attack(self, die_str):
        split_string = die_str.split("d")
        if len(split_string) != 2:
            raise ValueError("invalid die string supplied, check json for basic attack")
        return {"num_die": int(split_string[0]), "sides": int(split_string[1])}

class Player(Character):

    def __init__(self, level, hit_die, con, strength, dex, intel, wis, ris, ac, name, base_attack):
        base_hp = hit_die + self.get_modifier(con)
        self.current_hp_per_level = (hit_die // 2) + 1 + self.get_modifier(con)
        self.hit_die = hit_die
        self.name = name
        if level > 1:
            total_health = base_hp + (self.current_hp_per_level * (level - 1))
        else:
            total_health = base_hp
        super().__init__(level, total_health, con, strength, dex, intel, wis, ris, ac, base_attack)
    
    def update_level_health(self):
        base_hp = self.hit_die + self.get_modifier(self.con)
        self.current_hp_per_level = (self.hit_die // 2) + 1 + self.get_modifier(self.con)
        self.max_hp = base_hp + (self.current_hp_per_level * (self.level - 1))

    def update_player_ac(self, new_ac, armor_mod):
        if self.get_modifier(self.dex) > armor_mod:
            self.ac = new_ac + armor_mod
        else:
            self.ac = new_ac + self.get_modifier(self.dex)

class EnemyNPC(Character):
    def __init__(self, level, max_hp, con, strength, dex, intel, wis, ris, ac, name, base_attack, ability_use_chance):
        super().__init__(level, max_hp, con, strength, dex, intel, wis, ris, ac, base_attack)
        self.ability_use_chance = ability_use_chance
        self.name = name