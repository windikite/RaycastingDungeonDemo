import random, pygame
from utils import *
# from classes import *
from effects import *
from actionMenu import ActionMenu


class BattleController:
    INIT, PLAYER_WAIT, PLAYER_ACTION, ENEMY_ACTION, CLEANUP = range(5)

    def __init__(self, game, party, enemies):
        self.game = game
        self.party = party
        self.enemies = enemies
        self.turn_order = []
        self.current    = 0
        self.state      = self.INIT
        self.party_menu = ActionMenu(game, self, self.party)
        self.selection = None
        self.selection_target = None
        self.message_queue = []
        self.party_menu.generate_menu_options()
        self.game.UI.create_sprites(self.party, self.enemies)
        # self.game.UI.show_one_party_sprite(0)
        # self.game.UI.show_one_enemy_sprite(0)
        
    def determine_initiative(self):
        self.add_messages("rolling initiative...")
        self.turn_order = sorted(
            self.party + self.enemies,
            key=lambda c: c.stats["spd"],
            reverse=True
        )
    
    def end_battle(self):
        self.game.state = "EXPLORE"
        self.game.battle = None
    
    def update(self, dt):
        if self.state == self.INIT:
            self.determine_initiative()
            self.state = self.PLAYER_WAIT

        elif self.state == self.PLAYER_WAIT:
            if self.selection is not None:
                self.state = self.PLAYER_ACTION

        elif self.state == self.PLAYER_ACTION:
            actor = self.turn_order[self.current]
            target = self.selection_target
            attack_message, current_health, damage_message = actor.attack(target)
            self.add_messages([attack_message, damage_message])
            self.clear_selection()
            self.state = self.ENEMY_ACTION

        elif self.state == self.ENEMY_ACTION:
            actor = self.turn_order[self.current]
            if not actor.get_party():
                self._run_ai(actor)
            self.current = (self.current + 1) % len(self.turn_order)
            if self._check_victory():
                self.state = self.CLEANUP
            else:
                self.state = self.PLAYER_WAIT

        elif self.state == self.CLEANUP:
            self.end_battle()
        self.game.UI.update(dt)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.message_queue:
                if event.key == pygame.K_SPACE:
                    self.clear_messages()
                return
            if self.state == self.PLAYER_WAIT:
                if event.key == pygame.K_UP:
                    self.party_menu.move_select_up()
                elif event.key == pygame.K_DOWN:
                    self.party_menu.move_select_down()
                elif event.key == pygame.K_SPACE:
                    self.party_menu.confirm()
                # elif event.key == pygame.K_LEFT:
                #     self.party_menu.cycle_up()
                # elif event.key == pygame.K_LEFT:
                #     self.party_menu.cycle_up()

    def render(self):
        self.game.UI.draw_battlefield()
        if self.enemies:
            self.game.UI.draw_sprites()
        if self.message_queue:
            self.game.UI.draw_message_box(self.message_queue)
        else:
            if self.state == self.PLAYER_WAIT:
                self.game.UI.draw_player_menu(self.party_menu.current_menu_slot_index, self.party_menu.options)

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
    
    def clear_messages(self):
        self.message_queue.clear()
    
    def add_messages(self, messages):
        self.clear_messages()
        if isinstance(messages, (str, int)):
            self.message_queue.append(messages)
        elif isinstance(messages, list):
            for message in messages:
                self.message_queue.append(message)
        else:
            self.message_queue.append('Failed to get message!')
            

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
    #                         Heal(char, self.party[party_target_index], 2)
    #                         sub_menu = 0
    #                         i = 0
    #                         break
    #                 if sub_menu == 2:
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