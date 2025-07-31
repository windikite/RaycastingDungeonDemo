import pygame
from action import Action
from effects import *

class ActionMenu:
    def __init__(self, game, battle, party):
        self.game = game
        self.battle = battle
        self.party = party
        self.current_character = self.party[0]
        self.menu = 'Main'
        self.options = []
        self.current_menu_slot_index = 0
        self.selection        = None
        self.current_party_slot_index = 0
        self.current_enemy_slot_index = 0
        self.selection_target = None

    def package_option(self, action_name, callback):
        return Action(action_name, callback)

    def generate_menu_options(self):
        if self.menu == 'Main':
            self.options = ['Attack', 'Magic', 'Items', 'Flee']
        elif self.menu == 'Magic':
            self.options = [action.get_name() for action in self.current_character.magic.get_items()]
            print(self.options)
        elif self.menu == 'Items':
            self.options = [item.item.get_name() for item in self.current_character.inventory.get_items()]
        elif self.menu == 'Enemies':
            self.options = [enemy.get_name() for enemy in self.battle.enemies]
        elif self.menu == 'Party':
            self.options = [char.get_name() for char in self.party]
        return self.options
    
    def generate_party_options(self):
        party_options = [self.generate_menu_options(x) for x in self.party]
        return zip(self.party, party_options)
    
    def clear_menu_position(self):
        self.menu = 'Main'
    
    def clear_current_menu_slot_index(self):
        self.current_menu_slot_index = 0

    def clear_current_enemy_slot_index(self):
        self.current_enemy_slot_index = 0
    
    def clear_current_party_slot_index(self):
        self.current_party_slot_index = 0

    def clear_selection(self):
        self.selection = None
        self.selection_target = None
    
    def move_select_up(self):
        if self.current_menu_slot_index > 0:
            self.current_menu_slot_index -= 1
            if self.menu == "Enemies":
                self.cycle_enemy_up()
            elif self.menu == "Party":
                self.cycle_party_up()
    
    def move_select_down(self):
        if self.current_menu_slot_index < len(self.options) - 1:
            self.current_menu_slot_index += 1
            if self.menu == "Enemies":
                self.cycle_enemy_down()
            elif self.menu == "Party":
                self.cycle_party_down()
    
    # def update_visible_enemy_sprite(self):
    #     self.game.UI.show_one_enemy_sprite(self.current_enemy_slot_index)

    def cycle_party_up(self):
        if self.current_party_slot_index > 0:
            self.current_party_slot_index -= 1
    
    def cycle_party_down(self):
        if self.current_party_slot_index < len(self.party) - 1:
            self.current_party_slot_index += 1
    
    def cycle_enemy_up(self):
        if self.current_enemy_slot_index > 0:
            self.current_enemy_slot_index -= 1
            # self.update_visible_enemy_sprite()
    
    def cycle_enemy_down(self):
        if self.current_enemy_slot_index < len(self.battle.enemies) - 1:
            self.current_enemy_slot_index += 1
            # self.update_visible_enemy_sprite()
    
    def get_valid_targets(self):
        if self.selection.can_target == 'Enemies':
            return self.battle.enemies
        elif self.selection.can_target == 'Party':
            return self.party
        elif self.selection.can_target == 'All':
            return [*self.party, *self.battle.enemies]
    
    def confirm(self):
        if self.selection == None:
            if self.menu == 'Main':
                if self.current_menu_slot_index == 0:
                    self.selection = self.current_character.weapon_attack
                    self.menu = 'Targets'
                elif self.current_menu_slot_index == len(self.options) -1:
                    self.battle.end_battle()
                else:
                    self.menu = self.options[self.current_menu_slot_index]
            elif self.menu == 'Magic':
                if len(self.current_character.magic.get_items()) >= 1:
                    self.selection = self.current_character.magic.get_items()[self.current_menu_slot_index]
                    self.menu = 'Targets'
            elif self.menu == 'Items':
                if len(self.current_character.inventory.get_items()) >= 1:
                    self.selection = self.current_character.inventory.get_items()[self.current_menu_slot_index]
                    self.menu = 'Targets'
            if self.selection != None:
                self.options = self.get_valid_targets()
        else:
            if self.menu == 'Targets':
                result = self.selection.activate(self.current_character, self.options[self.current_menu_slot_index])
                print(result)
                self.battle.add_messages(result)
            self.clear_selection()
            self.clear_menu_position()
            self.clear_current_enemy_slot_index()
            self.clear_current_party_slot_index()
        self.clear_current_menu_slot_index()
        self.generate_menu_options()