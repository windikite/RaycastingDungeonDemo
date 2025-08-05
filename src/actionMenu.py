import pygame
from action import Action
from effects import *
from turn import Turn

class ActionMenu:
    def __init__(self, game, mag):
        self.game = game
        self.mag = mag
        self.current_character = None
        self.menu = 'Main'
        self.options = []
        self.current_menu_slot_index = 0
        self.selection        = None
        self.current_party_slot_index = 0
        self.current_enemy_slot_index = 0
        self.selection_target = None

        self.mag.subscribe("battle:initialized", self.initialize_menu)
        self.mag.subscribe("character:change", self.change_character)
        self.mag.subscribe("player:input", self.handle_input)

    def package_option(self, action_name, callback):
        return Action(action_name, callback)
    
    def change_character(self, char):
        self.current_character = char
        self.generate_menu_options()
        self.publish_menu()
        self.mag.publish("battlemenu:show")

    def generate_menu_options(self):
        if self.menu == 'Main':
            self.options = ['Attack', 'Magic', 'Items', 'Flee']
        elif self.menu == 'Magic':
            self.options = [action.get_name() for action in self.current_character.magic.get_items()]
        elif self.menu == 'Items':
            self.options = [item.item.get_name() for item in self.current_character.inventory.get_items()]
        elif self.menu == 'Enemies':
            self.options = [enemy.get_name() for enemy in self.game.enemies]
        elif self.menu == 'Party':
            self.options = [char.get_name() for char in self.game.party]
        return self.options
    
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
    
    def initialize_menu(self):
        self.clear_menu_position()
        self.clear_selection()
        if self.current_character is not None:
            self.generate_menu_options()
            self.publish_menu()
    
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
    
    def cycle_party_up(self):
        if self.current_party_slot_index > 0:
            self.current_party_slot_index -= 1
    
    def cycle_party_down(self):
        if self.current_party_slot_index < len(self.game.party) - 1:
            self.current_party_slot_index += 1
    
    def cycle_enemy_up(self):
        if self.current_enemy_slot_index > 0:
            self.current_enemy_slot_index -= 1
    
    def cycle_enemy_down(self):
        if self.current_enemy_slot_index < len(self.game.enemies) - 1:
            self.current_enemy_slot_index += 1
    
    def get_valid_targets(self):
        if self.selection.can_target == 'Enemies':
            return self.game.enemies
        elif self.selection.can_target == 'Party':
            return self.game.party
        elif self.selection.can_target == 'All':
            return [*self.game.party, *self.game.enemies]
    
    def confirm(self):
        if self.selection == None:
            if self.menu == 'Main':
                if self.current_menu_slot_index == 0:
                    self.selection = self.current_character.weapon_attack
                    self.menu = 'Targets'
                elif self.current_menu_slot_index == len(self.options) -1:
                    self.mag.publish("battle:end")
                else:
                    self.menu = self.options[self.current_menu_slot_index]
            elif self.menu == 'Magic':
                if len(self.current_character.magic.get_items()) >= 1:
                    choice = self.current_character.magic.get_items()[self.current_menu_slot_index]
                    if choice.callback == None:
                        return
                    else:
                        self.selection = choice
                    self.menu = 'Targets'
            elif self.menu == 'Items':
                if len(self.current_character.inventory.get_items()) >= 1:
                    choice = self.current_character.inventory.get_items()[self.current_menu_slot_index]
                    if choice.callback == None:
                        return
                    else:
                        self.selection = choice
                    self.menu = 'Targets'
            if self.selection != None:
                self.options = self.get_valid_targets()
                self.mag.publish("atb:pause")
        else:
            turn = Turn(self.current_character, self.selection, self.options[self.current_menu_slot_index])
            self.current_character = None
            self.mag.publish("turnqueue:add", turn=turn)
            self.mag.publish("turn:packaged", char=self.current_character)
            self.mag.publish("battlemenu:hide")
            self.mag.publish("atb:unpause")
            self.clear_selection()
            self.clear_menu_position()
            self.clear_current_enemy_slot_index()
            self.clear_current_party_slot_index()
        self.clear_current_menu_slot_index()
        self.generate_menu_options()
    
    def publish_menu(self):
        self.mag.publish("menu:update", menu={
            "options":self.options,
            "current_character":self.current_character,
            "current_menu_slot_index":self.current_menu_slot_index,
            "selection":self.selection,
            "target":self.selection_target
        })
    
    def handle_input(self, e):
        if self.current_character:
            if e.key == pygame.K_UP:
                self.move_select_up()
            elif e.key == pygame.K_DOWN:
                self.move_select_down()
            elif e.key == pygame.K_SPACE:
                self.confirm()
            elif e.key == pygame.K_LEFT:
                pass
            elif e.key == pygame.K_RIGHT:
                pass
            self.publish_menu()