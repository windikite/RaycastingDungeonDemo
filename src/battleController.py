import random, pygame
from utils import *
from effects import *
from character import Character
from turn import Turn

class BattleController:
    def __init__(self, game, mag):
        self.game = game
        self.mag = mag
        self.enemy_templates = self.game.enemy_templates
        self.turn_delay_ms = 4000#time to delay while each action wraps up animations, etc
        self.current_character_index = 0
        self.turn_order = []
        self.atb_paused = False
        self.last_turn_ms = 0
        self.action_queue = []
        self.turn_queue = []
        self.menu_busy = False
        self.selection = None
        self.selection_target = None
        self.message_queue = []
        self.mag.subscribe("battle:start", self.initialize_battle)
        self.mag.subscribe("battle:input", self.handle_event)
        self.mag.subscribe("battle:update", self.update)
        self.mag.subscribe("battle:end", self.end_battle)
        self.mag.subscribe("atb:pause", self.pause_atb)
        self.mag.subscribe("atb:unpause", self.unpause_atb)
        self.mag.subscribe("turn:packaged", self.handle_menu_ready)
        self.mag.subscribe("turnqueue:add", self.add_turn_to_queue)
    
    def generate_encounter(self):
        selected_enemy_indices = RandomSelect(len(self.enemy_templates), 3, True)
        selected_enemies = [Character(self.game, self.enemy_templates[x]) for x in selected_enemy_indices]
        self.game.enemies = selected_enemies
        self.mag.publish("enemies:created", enemies=selected_enemies)
        return selected_enemies
        
    def determine_initiative(self):
        self.turn_order = sorted(
            self.game.party + self.game.enemies,
            key=lambda c: c.stats["spd"],
            reverse=True
        )
    
    def initialize_battle(self):
        self.generate_encounter()
        self.determine_initiative()
        self.mag.publish("battle:initialized")
    
    def end_battle(self):
        self.mag.publish("state:change")
        self.mag.publish("explore:start")

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN:
            self.mag.publish("player:input", e=e)
    
    def progress_atb(self, dt):
        party_alive, enemy_alive = self.get_living_characters()
        sorted_alive = sorted(
            party_alive + enemy_alive,
            key=lambda c: c.stats["spd"],
            reverse=True
        )
        for x in sorted_alive:
            prev = x.atb_ms
            x.atb_ms = min(prev + (dt * 1000), x.cooldown_ms)
            if prev <= x.cooldown_ms and x.atb_ms == x.cooldown_ms:
                if any(char.id == x.id for char in self.action_queue) == False:
                    if any(t.character.id == x.id for t in self.turn_queue) == False:
                        self.mag.publish("character:ready", char=x)
                        self.action_queue.append(x)

    def pause_atb(self):
        self.atb_paused = True
    
    def unpause_atb(self):
        self.atb_paused = False
    
    def get_ready_characters(self):
        party_alive, enemy_alive = self.get_living_characters()
        party_ready = [x for x in party_alive if x.atb_ms == x.cooldown_ms]
        enemy_ready = [x for x in enemy_alive if x.atb_ms == x.cooldown_ms]
        return party_ready, enemy_ready
    
    def update(self, dt, time):
        # check for victory or defeat
        if (time - self.last_turn_ms >= self.turn_delay_ms):
            end = self.check_victory()
            if end:
                self.end_battle()
        #remove all dead characters from action queue and purge their turns
        self.action_queue = [
        c for c in self.action_queue
            if c.get_stats()["cur_health"] > 0
        ]
        self.turn_queue   = [
            t for t in self.turn_queue
            if t.character.get_stats()["cur_health"] > 0
        ]
        # progress all atb by dt
        if self.atb_paused == False:
            self.progress_atb(dt)
        # handle earliest ready character turn creation
        if len(self.action_queue) > 0:
            acting_character = self.action_queue[0]
            if acting_character.is_party == True and self.menu_busy == False:
                self.mag.publish("character:change", char=acting_character)
                self.menu_busy = True
            elif acting_character.is_party == False:
                self.run_enemy_ai(acting_character)
            self.remove_from_action_queue(acting_character)
        # handle resolution of turn if there is an open game state
        if len(self.turn_queue) > 0 and (time - self.last_turn_ms >= self.turn_delay_ms):
            self.resolve_turn(self.turn_queue[0])
    
    def resolve_turn(self, turn):
        attack_message, current_health, damage_message = turn.resolve_turn()
        self.add_messages([attack_message, damage_message])
        self.remove_turn_from_queue(turn)
        self.last_turn_ms = self.game.time
        if current_health == 0:
            self.mag.publish("character:dead", char=turn.target)
        
    def handle_menu_ready(self, char):
        self.menu_busy = False
                
    def get_living_characters(self):
        party_alive = [x for x in self.game.party if x.get_stats()["cur_health"] > 0]
        enemy_alive = [x for x in self.game.enemies if x.get_stats()["cur_health"] > 0]
        return party_alive, enemy_alive
    
    def remove_from_action_queue(self, char_to_remove):
        found_char = next((c for c in self.action_queue if c.id == char_to_remove.id), None)
        if found_char is not None:
            self.action_queue.remove(found_char)
            return True
        return False
    
    def add_turn_to_queue(self, turn):
        self.turn_queue.append(turn)
    
    def remove_turn_from_queue(self, turn):
        found_turn = next((t for t in self.turn_queue if t.character.name == turn.character.name), None)
        if found_turn:
            self.turn_queue.remove(found_turn)

    def run_enemy_ai(self, char):
        party_alive, enemy_alive = self.get_living_characters()
        if party_alive:
            random_choice = random.choice(party_alive)
            turn = Turn(char, char.weapon_attack, random_choice)
            self.add_turn_to_queue(turn)

    def check_victory(self):
        if not any(c.stats["cur_health"]>0 for c in self.game.enemies):
            self.add_messages("Party wins!")
            return True
        if not any(c.stats["cur_health"]>0 for c in self.game.party):
            self.add_messages("Enemies win!")
            return True
        return False
    
    def clear_selection(self):
        self.selection = None
        self.selection_target = None
    
    def add_messages(self, messages):
        self.mag.publish("messages:add", messages=messages)
            