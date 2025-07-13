from utils import *
from effects import *
import random
import pygame

class Entity:
    registry = []
    _global_id = 0

    def __init__(self, name):
        self.id   = Entity._global_id
        Entity._global_id += 1
        self.name = name
        Entity.registry.append(self)
        
    def get_id(self):
        return self.id
        
    def get_name(self):
        return self.name
        
class Character(Entity):
    def __init__(self, name, max_health=1, att=0, res=0, spd=0, party=False):
        super().__init__(name)
        self.stats = {"max_health": max_health, "cur_health": max_health, "att": att, "res": res, "spd": spd}
        self.inventory = Inventory()
        self.is_party = party
        
    def get_stats(self):
        return self.stats
    
    def get_party(self):
        return self.is_party
        
    def take_damage(self, amount):
        cur = self.stats["cur_health"]
        res = self.stats["res"]
        effective_damage = max(amount - res, 0)
        if(cur - effective_damage <= 0):
            cur = 0
            print(f'{self.name} took {effective_damage} damage! {res} damage was resisted. {self.name} has been slain!')
        else:
            cur -= effective_damage
            print(f'{self.name} took {effective_damage} damage! {res} damage was resisted. {cur} health remaining!')
        self.stats["cur_health"] = cur
        return cur
        
    def attack(self, enemy, damage="none"):
        print(f'{self.name} attacked {enemy.name}!')
        if(damage == "none"): damage = self.stats["att"]
        start_h = enemy.get_stats()["cur_health"]
        cur_h = enemy.take_damage(damage)
        return cur_h
        
    def set_hp(self, amount):
        cur = self.stats["cur_health"]
        max = self.stats["max_health"]
        if(cur + amount > max):
            cur = max
        else:
            cur += amount
        self.stats["cur_health"] = cur
        return cur

class Item(Entity):
    def __init__(self, name, value=0, rarity="common", text="", effect=None):
        super().__init__(name)
        self.value = value
        self.rarity = rarity
        self.text = text
        self.effect = effect
    
    def get_value(self):
        return self.value
    
    def get_rarity(self):
        return self.rarity
    
    def get_text(self):
        return self.text
        
    def activate(self, source, target, **kwargs):
        if not self.effect:
            print(f"{self.name} does nothing.")
            return None
        return self.effect(source, target, **kwargs)

class ItemStack:
    def __init__(self, item, quantity=1):
        self.item     = item        
        self.quantity = quantity    

    def add(self, amount=1):
        self.quantity += amount

    def remove(self, amount=1):
        self.quantity = max(self.quantity - amount, 0)

    def is_empty(self):
        return self.quantity <= 0

    def __repr__(self):
        return f"<{self.quantity}× {self.item.name}>"

class Inventory:
    def __init__(self):
        self.slots = []  

    def add_item(self, item, qty=1):
        for stack in self.slots:
            if stack.item.id == item.id:
                stack.add(qty)
                return
        self.slots.append(ItemStack(item, qty))

    def remove_item(self, item, qty=1):
        for stack in self.slots:
            if stack.item.id == item.id:
                stack.remove(qty)
                if stack.is_empty():
                    self.slots.remove(stack)
                return

    def __repr__(self):
        return ", ".join(str(s) for s in self.slots)

class Battle:
    def __init__(self, game, party, enemies):
        self.party = party
        self.enemies = enemies
        self.turn_order = []
        self.turn_index = 0
        self.game = game
        
    def determine_initiative(self):
        print("rolling initiative...")
        turn_queue = self.party + self.enemies
        turn_queue.sort(key=lambda c: c.stats["spd"], reverse=True)
        self.turn_order = turn_queue
    
    def handle_ai(self, char, attackers, defenders):
        mh = char.get_stats()["max_health"]
        ch = char.get_stats()["cur_health"]
        if((ch / mh) * 100  <= 30 ):
            chance_to_heal = 40
            if(random.randint(1, 100) <= chance_to_heal):
                Heal(char, char, math.ceil(mh * 0.15))
                return
            else:
                print(f'{char.get_name()} failed to heal!')
        elif(char.get_party() == True and random.randint(1, 100) <= 10):
            Starshower(char, defenders)
        else:
            valid_defenders = [d for d in defenders if d.stats["cur_health"] > 0]
            attack_indices = RandomSelect(len(valid_defenders), 1)
            for x in attack_indices:
                remaining_health = char.attack(valid_defenders[x])
    
    def handle_turn(self, char):
        if(char.get_stats()["cur_health"] != 0):
            if(char.get_party() == False):
                self.handle_ai(char, self.enemies, self.party)
            else:
                self.handle_ai(char, self.party, self.enemies)
        self.next_turn()
        
    def next_turn(self):
        ti = self.turn_index
        if(ti != len(self.turn_order) - 1):
            ti += 1
        else:
            ti = 0
        self.turn_index = ti
    
    def start_battle(self):
        print("battle started!")
        self.determine_initiative()
            
        while ( any(x.stats["cur_health"] > 0 for x in self.party) and any(x.stats["cur_health"] > 0 for x in self.enemies) ):
            self.handle_turn(self.turn_order[self.turn_index])

        if any(x.stats["cur_health"] > 0 for x in self.party):
            survivors = [x.get_name() for x in self.party if x.get_stats()["cur_health"] > 0]
            survivor_text = (" and ").join(survivors)
            print(f'Party wins! {survivor_text} survived.')
        else:
            survivors = [x.get_name() for x in self.enemies if x.get_stats()["cur_health"] > 0]
            survivor_text = (" and ").join(survivors)
            print(f'Enemies won! {survivor_text} survived.')

        # self.game.clear_battle()

class Game:
    def __init__(self):
        self.party = []
        self.enemy_templates = []
        self.items = []
        self.active_battle = None
    
    def create_character(self, *args, **kw):
        new_char = Character(*args, **kw)
        if(new_char.get_party() == True):
            self.party.append(new_char)
    
    def create_item(self, *args, **kw):
        new_item = Item(*args, **kw)
        self.items.append(new_item)
    
    def create_battle(self):
        new_battle = Battle(self, self.party, self.generate_encounter())
        self.active_battle = new_battle
        print(self.active_battle)
        self.active_battle.start_battle()
    
    def generate_encounter(self):
        selected_enemy_indices = RandomSelect(len(self.enemy_templates), 3, True)
        selected_enemies = [Character(*self.enemy_templates[x]) for x in selected_enemy_indices]
        return selected_enemies
    
    def check_encounter(self, chance):
        is_encounter = True if (random.randint(1, 100) > (100 - chance)) else False
        if(is_encounter):
            self.create_battle()
    
    def clear_battle(self):
        self.active_battle = None
    
    def get_active_battle(self):
        return self.active_battle

class UI:
    def __init__(self, screen_size):
        # unpack once in the constructor
        self.screen_width, self.screen_height = screen_size

    def draw_button(
        self,
        surface,        # the target Surface
        pos,            # (x, y) top-left of button
        size,           # (w, h) dimensions
        text,           # text to render
        font,           # pygame.font.Font
        idle_color,     # bg when not hovered
        hover_color,    # bg when hovered
        click_color,    # bg when clicked
        border_color,   # button border
        mouse_pos,      # pygame.mouse.get_pos()
        mouse_click     # pygame.mouse.get_pressed()[0]
    ):
        x, y    = pos
        w, h    = size
        bt, br  = 3, 8   # border thickness, border radius

        # 1) hover / click detection
        hovered = (x <= mouse_pos[0] <= x + w
                   and y <= mouse_pos[1] <= y + h)
        clicked = hovered and mouse_click

        # 2) choose background color
        if   clicked: bg = click_color
        elif hovered: bg = hover_color
        else:         bg = idle_color

        # 3) draw border + fill
        pygame.draw.rect(surface, border_color, (x, y, w, h), border_radius=br)
        inner = (x+bt, y+bt, w-2*bt, h-2*bt)
        pygame.draw.rect(surface, bg, inner, border_radius=br-1)

        # 4) render & center text
        ts = font.render(text, True, (255,255,255))
        tr = ts.get_rect(center=(x + w//2, y + h//2))
        surface.blit(ts, tr)

        return clicked

    def draw_combat_bar(
        self,
        surface,
        mouse_pos,
        mouse_click,
        font,
        callback=None
    ):
        """
        Draws the bottom “combat bar” and an End-Combat button.
        Returns True if the button was clicked.
        """
        # 1) bar background
        bar_h   = int(self.screen_height * 0.3)
        bar_y   = self.screen_height - bar_h
        pygame.draw.rect(surface, (20, 255, 255),
            (0, bar_y, self.screen_width, bar_h))

        # 2) button geometry
        btn_w, btn_h = 200, 60
        btn_x = (self.screen_width - btn_w) // 2
        btn_y = bar_y + (bar_h - btn_h) // 2

        # 3) draw the button
        clicked = self.draw_button(
            surface     = surface,
            pos         = (btn_x, btn_y),
            size        = (btn_w, btn_h),
            text        = "End Combat",
            font        = font,
            idle_color  = (70, 70, 70),
            hover_color = (100,100,100),
            click_color = (150,150,150),
            border_color= (255,255,255),
            mouse_pos   = mouse_pos,
            mouse_click = mouse_click
        )

        # 4) optionally invoke a callback
        if clicked and callback:
            callback()

        return clicked

    def draw_dungeon_ui(
        self, surface,
        mouse_pos, mouse_click,
        font,
        on_party=None,
        on_items=None
    ):
        # 1) draw the bar
        bar_h = int(self.screen_height * 0.1)
        bar_y = self.screen_height - bar_h
        pygame.draw.rect(surface, (20,0,20),
                         (0, bar_y, self.screen_width, bar_h))

        # 2) decide button sizes and padding
        btn_h   = bar_h - 16              # vertical padding of 8px top/bottom
        btn_w   = 120                     # you can adjust for text width
        padding = 16

        # 3) compute each button's top-left
        #    Party button at left
        party_pos = (
            padding,
            bar_y + (bar_h - btn_h)//2
        )
        #    Items button to the right of it
        items_pos = (
            padding*2 + btn_w,
            bar_y + (bar_h - btn_h)//2
        )

        # 4) draw & detect clicks
        clicked_party = self.draw_button(
            surface, party_pos, (btn_w, btn_h),
            "Party", font,
            idle_color  = (70,70,70),
            hover_color = (100,100,100),
            click_color = (150,150,150),
            border_color= (255,255,255),
            mouse_pos   = mouse_pos,
            mouse_click = mouse_click
        )
        if clicked_party and on_party:
            on_party()

        clicked_items = self.draw_button(
            surface, items_pos, (btn_w, btn_h),
            "Items", font,
            idle_color  = (70,70,70),
            hover_color = (100,100,100),
            click_color = (150,150,150),
            border_color= (255,255,255),
            mouse_pos   = mouse_pos,
            mouse_click = mouse_click
        )
        if clicked_items and on_items:
            on_items()

        return clicked_party, clicked_items