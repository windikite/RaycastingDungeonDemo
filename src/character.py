from entity import Entity
from inventory import Inventory
from effects import *
from action import Action
from spellCompendium import SpellCompendium

class Character(Entity):
    def __init__(self, game, character_data):
        super().__init__(character_data["name"])
        self.game = game
        self.stats = {
            "max_health": character_data["max_health"], 
            "cur_health": character_data["cur_health"], 
            "att": character_data["attack"], 
            "res": character_data["resistance"], 
            "spd": character_data["speed"]
        }
        self.weapon_attack = Action("Greatsword", "Attack", Weapon_Attack, target_style="Single", can_target="Enemies")
        self.inventory = Inventory(self.game, character_data["inventory"])
        self.magic = SpellCompendium(self.game, character_data["magic"])
        self.is_party = character_data["is_party"]
        self.sprite = character_data["sprite"]
        self.atb_ms = 0
        self.cooldown_ms = 0
        
    def get_stats(self):
        return self.stats
    
    def get_party(self):
        return self.is_party
        
    def take_damage(self, amount):
        cur = self.stats["cur_health"]
        res = self.stats["res"]
        effective_damage = max(amount - res, 0)
        damage_message = ''
        if(cur - effective_damage <= 0):
            cur = 0
            damage_message = f'{self.name} took {effective_damage} damage! {res} damage was resisted. {self.name} has been slain!'
        else:
            cur -= effective_damage
            damage_message = f'{self.name} took {effective_damage} damage! {res} damage was resisted. {cur} health remaining!'
        self.stats["cur_health"] = cur
        return cur, damage_message
        
    def attack(self, enemy, damage="none"):
        attack_message = f'{self.name} attacked {enemy.name}!'
        if(damage == "none"): damage = self.stats["att"]
        start_h = enemy.get_stats()["cur_health"]
        current_health, damage_message = enemy.take_damage(damage)
        return attack_message, current_health, damage_message
        
    def set_hp(self, amount):
        current_health = self.stats["cur_health"]
        max_health = self.stats["max_health"]
        if(current_health + amount > max_health):
            current_health = max_health
        else:
            current_health += amount
        self.stats["cur_health"] = current_health
        return current_health

    def set_cooldown(self, cooldown_time):
        self.atb_ms = 0
        self.cooldown_ms = cooldown_time