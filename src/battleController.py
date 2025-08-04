import random, pygame
from utils import *
from effects import *
from character import Character


class BattleController:
    INIT, PLAYER_WAIT, PLAYER_ACTION, ENEMY_ACTION, CLEANUP = range(5)

    def __init__(self, game, mag):
        self.game = game
        self.mag = mag
        self.enemy_templates = self.game.enemy_templates
        self.party = self.game.party
        self.enemies = []
        self.current_character_index = 0
        self.state = self.INIT
        self.atb_paused = False
        self.selection = None
        self.selection_target = None
        self.message_queue = []
        self.mag.subscribe("battle:start", self.initialize_battle)
        self.mag.subscribe("battle:input", self.handle_event)
        self.mag.subscribe("battle:update", self.update)
        self.mag.subscribe("battle:end", self.end_battle)
        self.mag.subscribe("atb:pause", self.pause_atb)
        self.mag.subscribe("atb:unpause", self.unpause_atb)
    
    def generate_encounter(self):
        selected_enemy_indices = RandomSelect(len(self.enemy_templates), 3, True)
        selected_enemies = [Character(self.game, self.enemy_templates[x]) for x in selected_enemy_indices]
        self.game.enemies = selected_enemies
        self.mag.publish("enemies:created", enemies=selected_enemies)
        return selected_enemies
        
    def determine_initiative(self):
        self.turn_order = sorted(
            self.party + self.enemies,
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
        for x in (self.game.party + self.game.enemies):
            x.atb_ms = min(x.atb_ms + (dt * 1000), x.cooldown_ms)
    
    def pause_atb(self):
        self.atb_paused = True
    
    def unpause_atb(self):
        self.atb_paused = False
    
    def update(self, dt, time):
        if self.state == self.INIT:
            self.determine_initiative()
            self.state = self.PLAYER_WAIT

        elif self.state == self.PLAYER_WAIT:
            if self.selection is not None:
                self.state = self.PLAYER_ACTION

        elif self.state == self.PLAYER_ACTION:
            # actor = self.turn_order[self.current_character_index]
            # target = self.selection_target
            # attack_message, current_health, damage_message = actor.attack(target)
            # self.add_messages([attack_message, damage_message])
            # self.clear_selection()
            self.state = self.ENEMY_ACTION

        elif self.state == self.ENEMY_ACTION:
            actor = self.turn_order[self.current]
            if not actor.get_party():
                self._run_ai(actor)
            self.current_character_index = (self.current_character_index + 1) % len(self.turn_order)
            if self._check_victory():
                self.state = self.CLEANUP
            else:
                self.state = self.PLAYER_WAIT
        elif self.state == self.CLEANUP:
            self.end_battle()
            if self.message_queue:
                if event.key == pygame.K_SPACE:
                    self.clear_messages()
                return
            if self.state == self.PLAYER_WAIT:
                pass
        if self.atb_paused == False:
            self.progress_atb(dt)

    def _run_ai(self, char):
        valid = [c for c in (self.party if not char.get_party() else self.enemies) if c.stats["cur_health"]>0]
        if valid:
            attack_message, current_health, damage_message = char.attack(random.choice(valid))
            self.add_messages([attack_message, damage_message])

    def _check_victory(self):
        if not any(c.stats["cur_health"]>0 for c in self.enemies):
            self.add_messages("Party wins!")
            return True
        if not any(c.stats["cur_health"]>0 for c in self.party):
            self.add_messages("Enemies win!")
            return True
        return False
    
    def clear_selection(self):
        self.selection = None
        self.selection_target = None
    
    def add_messages(self, messages):
        self.mag.publish("messages:add", messages=messages)
            

        # def handle_ai(self, char, attackers, defenders):
    #     mh = char.get_stats()["max_health"]
    #     ch = char.get_stats()["cur_health"]
    #     if((ch / mh) * 100  <= 30 ):
    #         chance_to_heal = 40
    #         if(random.randint(1, 100) <= chance_to_heal):
    #             Heal(char, char, math.ceil(mh * 0.15))
    #             return
    #         else:
    #             print(f'{char.get_name()} failed to heal!')
    #     elif(char.get_party() == True and random.randint(1, 100) <= 10):
    #         Starshower(char, defenders)
    #     else:
    #         valid_defenders = [d for d in defenders if d.get_stats()["cur_health"] > 0]
    #         attack_indices = RandomSelect(len(valid_defenders), 1)
    #         for x in attack_indices:
    #             remaining_health = char.attack(valid_defenders[x])
    
    # def handle_turn(self, char):    
    #     if(char.get_stats()["cur_health"] != 0):
    #         if(char.get_party() == False):
    #             self.handle_ai(char, self.enemies, self.party)
    #         else:
    #             battle_menu = ['Attack', 'Skills', 'Items', 'Shoot']
    #             skill_menu = ['Starshower', 'Great Lightning Spear', 'Last Light']
    #             i = 0
    #             sub_menu = 0
    #             while True:
    #                 for x in range(5):
    #                     print('')
    #                 print((' || ').join([f'{x.get_name()} - {x.get_stats()["cur_health"]}hp' for x in self.enemies]))
    #                 print(f'{char.get_name()}s turn!')
    #                 valid_defenders = [d for d in self.enemies if d.get_stats()["cur_health"] > 0]
    #                 if sub_menu == 0:
    #                     if int(i) == 0:
    #                         display_options(bf.gattle_menu)
    #                     if int(i) == 1:
    #                         enemy_target_index = RandomSelect(len(valid_defenders), 1, False)[0]
    #                         char.attack(valid_defenders[enemy_target_index])
    #                         i = 0
    #                         break
    #                     if int(i) == 2:
    #                         sub_menu = 1
    #                         i = 0
    #                     if int(i) == 3:
    #                         sub_menu = 2
    #                         i = 0
    #                 if sub_menu == 1:
    #                     if int(i) == 0:
    #                         display_options(skill_menu)
    #                     if int(i) == 1:
    #                         Starshower(char, self.enemies)
    #                         sub_menu = 0
    #                         i = 0
    #                         break
    #                     if int(i) == 2:
    #                         enemy_target_index = RandomSelect(len(valid_defenders), 1, False)[0]
    #                         Damage(char, valid_defenders[enemy_target_index], 5)
    #                         sub_menu = 0
    #                         i = 0
    #                         break
    #                     if int(i) == 3:
    #                         party_target_index = RandomSelect(len(self.party), 1, False)[0]
    #                         Heal(char, self.pa
    #                     if int(i) == 0:
    #                         char.inventory.add_item(self.game.items[0])
    #                         inventory = [str(x) for x in char.inventory.get_items()]
    #                         if(len(inventory) == 0):
    #                             print('None')
    #                             continue
    #                         display_options(inventory)
    #                     if int(i) > len(inventory):
    #                         i = 0
    #                         break
    #                     if int(i) > 0 and int(i) <= len(inventory):
    #                         party_target_index = RandomSelect(len(self.party), 1, False)[0]
    #                         char.inventory.get_items()[i-1].item.activate(char, self.party[party_target_index])
    #                         i = 0
    #                         break
    #                 i = int(input("Enter number and press enter:"))
    #     self.next_turn()
        
    # def next_turn(self):
        # self.game.UI.show_one_party_sprite(0)
        # self.game.UI.show_one_enemy_sprite(0)
    #     ti = self.turn_index
    #     if(ti != len(self.turn_order) - 1):
    #         ti += 1
    #     else:
    #         ti = 0
    #     self.turn_index = ti
    
    # def start_battle(self):
    #     print("battle started!")﻿
    #     self.determine_initiative()
            
    #     while ( any(x.get_stats()["cur_health"] > 0 for x in self.party) and any(x.get_stats()["cur_health"] > 0 for x in self.enemies) ):
    #         self.handle_turn(self.turn_order[self.turn_index])

    #     if any(x.get_stats()["cur_health"] > 0 for x in self.party):
    #         survivors = [x.get_name() for x in self.party if x.get_stats()["cur_health"] > 0]
    #         survivor_text = (" and ").join(survivors)
    #         print(f'Party wins! {survivor_text} survived.')
    #     else:
    #         survivors = [x.get_name() for x in self.enemies if x.get_stats()["cur_health"] > 0]
    #         survivor_text = (" and ").join(survivors)
    #         print(f'Enemies won! {survivor_text} survived.')
    #     self.end_battle()