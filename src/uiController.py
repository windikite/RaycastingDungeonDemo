import pygame, math
from fadableSprite import FadableSprite
from character import Character
from item import Item
from action import Action

class UI:
    def __init__(self, game, mag):
        self.game = game
        self.mag = mag
        self.WIDTH, self.HEIGHT = 1920, 1080
        self.RENDER_WIDTH, self.RENDER_HEIGHT = 320, 180
        self.render_surface = pygame.Surface((self.RENDER_WIDTH, self.RENDER_HEIGHT))
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.zbuf  = [float('inf')]*self.RENDER_WIDTH
        self.bounds= [(0,self.RENDER_HEIGHT)]*self.RENDER_WIDTH
        self.FOV = math.radians(60)
        self.TILE_SIZE = 64
        self.FONT_NAME = None   
        self.FONT_SIZE = 45
        self.font = pygame.font.Font(self.FONT_NAME, self.FONT_SIZE)
        self.enemy_sprites = []

        self.message_queue = []
        self.last_message_ms = 0.0

        self.options = []
        self.current_character = None
        self.current_menu_slot_index = None
        self.selection = None
        self.target = None
        
        self.show_player_battle_menu = False

        self.mag.subscribe("player:position", self.update_player_positioning)
        self.mag.subscribe("dungeon:render", self.render_dungeon_ui)
        self.mag.subscribe("battle:update", self.update_battle_ui)
        self.mag.subscribe("battle:render", self.render_battle_ui)
        self.mag.subscribe("enemies:created", self.setup_battle_ui)
        self.mag.subscribe("messages:add", self.add_to_message_queue)
        self.mag.subscribe("menu:update", self.update_player_menu)
        self.mag.subscribe("character:dead", self.fade_sprite)
        self.mag.subscribe("battlemenu:show", self.show_battle_menu)
        self.mag.subscribe("battlemenu:hide", self.hide_battle_menu)

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
            (self.screen_width / 3, bar_y, self.screen_width / 3, bar_h * .9))

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
        callback_1
    ):
        # 1) draw the bar
        bar_h = int(self.screen_height * 0.25)
        bar_y = self.screen_height - bar_h
        pygame.draw.rect(surface, (20,0,20), (0, bar_y, self.screen_width, bar_h))
        
        plate_width = self.screen_width / 3
        plate_height = self.screen_height / 4
        first_row = plate_height * 3
        self.draw_character_plate(surface, 0, first_row, plate_width, plate_height)
        self.draw_character_plate(surface, self.screen_width / 3, first_row, plate_width, plate_height)

        labels = ["Party Slot 1", "Party Slot 2", "Party Slot 3"]

        clicked_party_1, clicked_party_2, clicked_party_3 = [
            self.draw_button(
                surface     = surface,
                # compute x and y separately:
                pos         = (
                    self.screen_width/3 * (i - 1),
                    self.screen_height * .5
                ),
                size        = (self.screen_width / 3, self.screen_height / 4),
                text        = label,
                font        = font,
                idle_color  = (70, 70, 70),
                hover_color = (100, 100, 100),
                click_color = (150, 150, 150),
                border_color= (255, 255, 255),
                mouse_pos   = mouse_pos,
                mouse_click = mouse_click
            )
            for i, label in enumerate(labels, start=1)
        ]

        # clicked_party_1 = self.draw_button(
        #     surface     = surface,
        #     pos         = (0, self.screen_height / 4 * 3),
        #     size        = (self.screen_width / 3, self.screen_height / 4),
        #     text        = "Party Slot 1",
        #     font        = font,
        #     idle_color  = (70, 70, 70),
        #     hover_color = (100,100,100),
        #     click_color = (150,150,150),
        #     border_color= (255,255,255),
        #     mouse_pos   = mouse_pos,
        #     mouse_click = mouse_click
        # )

        if clicked_party_1 and callback_1:
            callback_1()
        
        if clicked_party_2 and callback_1:
            callback_1()
        
        if clicked_party_3 and callback_1:
            callback_1()

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
        # clicked_party = self.draw_button(
        #     surface, party_pos, (btn_w, btn_h),
        #     "Party", font,
        #     idle_color  = (70,70,70),
        #     hover_color = (100,100,100),
        #     click_color = (150,150,150),
        #     border_color= (255,255,255),
        #     mouse_pos   = mouse_pos,
        #     mouse_click = mouse_click
        # )
        # if clicked_party and on_party:
        #     on_party()

        # clicked_items = self.draw_button(
        #     surface, items_pos, (btn_w, btn_h),
        #     "Items", font,
        #     idle_color  = (70,70,70),
        #     hover_color = (100,100,100),
        #     click_color = (150,150,150),
        #     border_color= (255,255,255),
        #     mouse_pos   = mouse_pos,
        #     mouse_click = mouse_click
        # )
        # if clicked_items and on_items:
        #     on_items()

        return clicked_party_1
    
    def draw_character_plate(self, surface, plate_x, plate_y, plate_width, plate_height):
        pygame.draw.rect(surface, (20,20,20), (plate_x, plate_y, plate_width, plate_height))
    
    def cast_rays(self, surface, z_buffer, wall_bounds):

        for ray in range(self.RENDER_WIDTH):
            ray_angle = self.player_angle - self.FOV/2 + (ray / self.RENDER_WIDTH) * self.FOV
            cos_a = math.cos(ray_angle)
            sin_a = math.sin(ray_angle)

            map_x = int(self.player_x // self.TILE_SIZE)
            map_y = int(self.player_y // self.TILE_SIZE)

            delta_dist_x = abs(self.TILE_SIZE / (cos_a if cos_a != 0 else 1e-6))
            delta_dist_y = abs(self.TILE_SIZE / (sin_a if sin_a != 0 else 1e-6))

            if cos_a < 0:
                step_x = -1
                side_dist_x = (self.player_x - map_x * self.TILE_SIZE) / (abs(cos_a) if cos_a != 0 else 1e-6)
            else:
                step_x = 1
                side_dist_x = ((map_x + 1) * self.TILE_SIZE - self.player_x) / (abs(cos_a) if cos_a != 0 else 1e-6)

            if sin_a < 0:
                step_y = -1
                side_dist_y = (self.player_y - map_y * self.TILE_SIZE) / (abs(sin_a) if sin_a != 0 else 1e-6)
            else:
                step_y = 1
                side_dist_y = ((map_y + 1) * self.TILE_SIZE - self.player_y) / (abs(sin_a) if sin_a != 0 else 1e-6)

            # DDA
            while True:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1

                dungeon_map = self.game.dungeon_controller.dungeon_map
                if not (0 <= map_x < len(dungeon_map[0]) and 0 <= map_y < len(dungeon_map)):
                    break
                if dungeon_map[map_y][map_x] == 1:
                    break

            if side == 0:
                depth = side_dist_x - delta_dist_x
            else:
                depth = side_dist_y - delta_dist_y

            corrected_depth = depth * math.cos(ray_angle - self.player_angle)
            z_buffer[ray] = corrected_depth

            wall_height = (self.RENDER_HEIGHT * 60) / (corrected_depth + 0.0001)
            wall_top = max(0, int(self.RENDER_HEIGHT/2 - wall_height/2))
            wall_bottom = min(self.RENDER_HEIGHT, int(self.RENDER_HEIGHT/2 + wall_height/2))
            wall_bounds[ray] = (wall_top, wall_bottom)

            shade = max(0.2, 1 / (1 + corrected_depth * 0.01))
            color = tuple(int(c * shade) for c in (54, 62, 82))
            surface.fill(color, rect=(ray, wall_top, 1, wall_bottom - wall_top))
    
    def draw_floor_and_ceiling(self, surface):

        mid = self.RENDER_HEIGHT // 2

        ray_x0 = math.cos(self.player_angle - self.FOV/2)
        ray_y0 = math.sin(self.player_angle - self.FOV/2)
        ray_x1 = math.cos(self.player_angle + self.FOV/2)
        ray_y1 = math.sin(self.player_angle + self.FOV/2)
        px, py = self.player_x / self.TILE_SIZE, self.player_y / self.TILE_SIZE

        for y in range(mid + 1, self.RENDER_HEIGHT):
            p = y - mid            
            row_dist = (self.TILE_SIZE * mid) / p

            brightness = max(0.1, min(1.0, 1 / (1 + row_dist * 0.01)))
            floor_color = tuple(int(c * brightness) for c in (41, 43, 48))
            ceil_color  = tuple(int(c * brightness) for c in (17, 20, 28))

            pygame.draw.line(surface, floor_color, (0,      y), (self.RENDER_WIDTH, y))
            pygame.draw.line(surface, ceil_color, (0, self.RENDER_HEIGHT - y - 1), (self.RENDER_WIDTH, self.RENDER_HEIGHT - y - 1))

    def draw_dungeon_geometry(self):
        surf = pygame.Surface((self.RENDER_WIDTH, self.RENDER_HEIGHT))
        self.render_surface.fill((0,0,0))
        self.draw_floor_and_ceiling(self.render_surface)
        self.zbuf[:]   = [float('inf')]*self.RENDER_WIDTH
        self.bounds[:] = [(0,self.RENDER_HEIGHT)]*self.RENDER_WIDTH
        self.cast_rays(self.render_surface, self.zbuf, self.bounds)
        self.screen.blit(pygame.transform.scale(self.render_surface, (self.WIDTH, self.HEIGHT)), (0,0))
    
    def draw_rectangle(self, h_pos, v_pos, width, height, box_color, border_color, border_width=2):
        rect = pygame.Rect(h_pos, v_pos, width, height)
        pygame.draw.rect(self.screen, box_color, rect)
        pygame.draw.rect(self.screen, border_color, rect, border_width)
        return rect
    

    def draw_battlefield(self):
        self.screen.fill((30, 10, 10))
    
    def draw_character_tile(self, tile_box_h, tile_box_v, tile_box_width, tile_box_height, tile_box_color, box_border_color):
        tile_box_h = 0
        tile_box_v = self.HEIGHT - self.HEIGHT * 0.33
        tile_box_width = self.WIDTH
        tile_box_height = self.HEIGHT * 0.33
        tile_box_color = (30, 30, 30)
        box_border_color = (200, 200, 200)
        tile = self.draw_rectangle(tile_box_h, tile_box_v, tile_box_width, tile_box_height, tile_box_color, box_border_color)
    
    def write_text_within_box(self, rect, text, text_color, h_padding=10, v_padding=10, line_spacing=5):
        strings_to_write = text if isinstance(text, list) else [text]
        x = rect.x + h_padding
        y = rect.y + v_padding
        for string in strings_to_write:
            # if y + self.FONT_SIZE > rect.bottom - padding:
            #     break
            text_surf = self.font.render(string, True, text_color)
            self.screen.blit(text_surf, (x, y))
            y += self.FONT_SIZE + line_spacing
    
    def draw_message_box(self, messages):
        # draw message box
        message_box_width = self.WIDTH * 0.75
        message_box_height = self.HEIGHT * 0.10
        message_box_h = (self.WIDTH / 2) - (message_box_width / 2)
        message_box_v = (self.HEIGHT * 0.1) - (message_box_height / 2)
        message_box_color = (30, 30, 30)
        box_border_color = (200, 200, 200)
        message_box = self.draw_rectangle(message_box_h, message_box_v, message_box_width, message_box_height, message_box_color, box_border_color)
        self.write_text_within_box(message_box, messages, (200, 200, 200))
    
    # def draw_grid_menu(self, group, options):
    #     # draw menu box
    #     menu_box_h = 0
    #     menu_box_v = self.HEIGHT - self.HEIGHT * 0.33
    #     menu_box_width = self.WIDTH
    #     menu_box_height = self.HEIGHT * 0.33
    #     menu_box_color = (30, 30, 30)
    #     box_border_color = (200, 200, 200)
    #     menu_box = self.draw_rectangle(menu_box_h, menu_box_v, menu_box_width, menu_box_height, menu_box_color, box_border_color)
    #     # draw individual tiles
    #     tile_width = menu_box_width / 3
    #     tile_height = menu_box_height / 2
    #     left_column = 0
    #     middle_column = tile_width
    #     right_column = tile_width * 2
    #     top_row = menu_box_v
    #     bottom_row = menu_box_v + tile_height
    #     party_tiles = [self.draw_rectangle(*x) for x in [
    #         [left_column, top_row, tile_width, tile_height, menu_box_color, box_border_color],
    #         [middle_column, top_row, tile_width, tile_height, menu_box_colselected_enemieslor, box_border_color],
    #         [middle_column, bottom_row, tile_width, tile_height, menu_box_color, box_border_color],
    #         [right_column, bottom_row, tile_width, tile_height, menu_box_color, box_border_color]
    #     ]]
    #     # write text for each character within their tile
    #     zipped_party_tiles = zip(group, party_tiles)update_player_menu
    #     for combo in zipped_party_tiles:
    #         char = combo[0]
    #         tile = combo[1]
    #         character_data = [
    #             char.get_name(), 
    #             f'HP: {char.get_stats()['cur_health']} / {char.get_stats()['max_health']}'
    #         ]
    #         self.write_text_within_box(tile, character_data, (200, 200, 200))
    
    
    def create_sprites(self, party, enemies):
        rect = self.screen.get_rect()
        self.enemy_sprites = pygame.sprite.Group(FadableSprite(char.id, char.sprite, ((rect.width / (len(enemies) + 1)) * i, rect.height / 4), size=(480, 480), default_alpha=255, orientation="front") for i, char in enumerate(enemies, start=1)) 
        self.party_sprites = pygame.sprite.Group(FadableSprite(char.id, char.sprite, ((rect.width / (len(party) + 1)) * i, rect.height * 0.75), default_alpha=255, orientation="back") for i, char in enumerate(party, start=1))

    def show_one_party_sprite(self, index):
        for i, spr in enumerate(self.party_sprites.sprites()):
            spr.set_target_alpha(255 if i == index else 0)
    
    def draw_sprites(self):
        if self.enemy_sprites:
            for spr in self.enemy_sprites.sprites():  
                self.screen.blit(spr.image, spr.rect)
        if self.party_sprites:
            for spr in self.party_sprites.sprites():  
                self.screen.blit(spr.image, spr.rect)
    
    def update_player_menu(self, menu):
        self.options = menu["options"]
        self.current_character = menu["current_character"]
        self.current_menu_slot_index = menu["current_menu_slot_index"]
        self.selection = menu["selection"]
        self.target = menu["target"]
    
    def draw_party_ui(self):
        slot_size = self.FONT_SIZE + (self.FONT_SIZE * 0.1)
        # draw party box
        party_box_width = self.WIDTH / 3
        party_box_height = slot_size * len(self.game.party)
        party_box_h = (self.WIDTH * 0.75) - (party_box_width / 2)
        party_box_v = self.HEIGHT - (party_box_height + (party_box_height * 0.1))
        party_box_color = (30, 30, 30)
        box_border_color = (100, 100, 100)
        party_box = self.draw_rectangle(party_box_h, party_box_v, party_box_width, party_box_height, party_box_color, box_border_color)
        # draw individual slots
        slot_height = self.FONT_SIZE + (self.FONT_SIZE * .10)
        bar_width = party_box.width / 5
        bar_height = party_box.height * 0.25
        bar_color = (20, 20, 20)
        bar_border_color = (0, 0, 0)
        bar_h = party_box.right - bar_width - 15
        #write text
        text_color = (255, 255, 255)
        # names
        party_character_strings = [f'{x.get_name()}' for x in self.game.party]
        party_names = self.write_text_within_box(party_box, party_character_strings, text_color, h_padding=10, v_padding=10, line_spacing=(self.FONT_SIZE * 0.1))
        # hp
        hp_column = party_box.width / 2
        party_character_strings = [f'{x.get_stats()["cur_health"]}' for x in self.game.party]
        party_hp = self.write_text_within_box(party_box, party_character_strings, text_color, h_padding=hp_column, v_padding=10, line_spacing=(self.FONT_SIZE * 0.1))
        #draw atb bars
        atb_column = party_box.width - bar_width
        time = self.game.time
        for i, x in enumerate(self.game.party, start=0):
            bar_v = party_box.top + ((slot_height * i) + bar_height / 2)
            self.draw_rectangle(bar_h, bar_v, bar_width, bar_height, bar_color, bar_border_color, border_width=1)
            progress = x.atb_ms / x.cooldown_ms if x.cooldown_ms > 0 else 0.0
            progress_color = (0, 255, 255)
            self.draw_rectangle(bar_h, bar_v, bar_width * min(max(progress, 0.0), 1.0), bar_height, progress_color, bar_border_color, border_width=1)
        # draw top plate
        name_plate_box = self.draw_rectangle(party_box_h, party_box_v - slot_height, party_box_width, slot_height, party_box_color, box_border_color)
        name_text = self.write_text_within_box(name_plate_box, ["Name"], text_color, h_padding=10, v_padding=10, line_spacing=(self.FONT_SIZE * 0.1))
        hp_text = self.write_text_within_box(name_plate_box, ["HP"], text_color, h_padding=hp_column, v_padding=10, line_spacing=(self.FONT_SIZE * 0.1))
        atb_text = self.write_text_within_box(name_plate_box, ["ATB"], text_color, h_padding=atb_column, v_padding=10, line_spacing=(self.FONT_SIZE * 0.1))

    def draw_player_menu(self):
        # draw menu box
        menu_box_width = self.WIDTH / 5
        menu_box_height = self.HEIGHT / 3
        menu_box_h = (self.WIDTH * 0.15) - (menu_box_width / 2)
        menu_box_v = (self.HEIGHT * 0.75) - (menu_box_height / 2)
        menu_box_color = (30, 30, 30)
        box_border_color = (100, 100, 100)
        menu_box = self.draw_rectangle(menu_box_h, menu_box_v, menu_box_width, menu_box_height, menu_box_color, box_border_color)
        # draw individual slots
        slot_color = (50, 50, 50)
        slot_width = menu_box_width
        slot_height = self.FONT_SIZE + (self.FONT_SIZE * .10)
        player_menu_option_names = [x.get_name() if isinstance(x, (Character, Action)) else f'{x.quantity}x {x.item.get_name()}' if isinstance(x, Item) else x for x in self.options]
        options_with_marking = [x+'<' if i == self.current_menu_slot_index else x for i,x in enumerate(player_menu_option_names)] 
        text_color = (255, 255, 255)
        option_menu = self.write_text_within_box(menu_box, options_with_marking, text_color)
        # draw name plate
        name_plate_box = self.draw_rectangle(menu_box_h, menu_box_v - slot_height, menu_box_width, slot_height, menu_box_color, text_color)
        char_name = self.current_character.name if self.current_character else ''
        name_text = self.write_text_within_box(name_plate_box, [char_name], text_color, h_padding=10, v_padding=10, line_spacing=(self.FONT_SIZE * 0.1))
        
        # action_slots = [self.draw_rectangle(*x) for i, x in enumerate(options)]
        # self.draw_grid_menu(self.game.battle.enemies, player_menu_options)
        # action_slots = [self.draw_rectangle(*x) for x in [
        #     [left_column, top_row, slot_width, slot_height, slot_color, box_border_color],
        #     [middle_column, top_row, slot_width, slot_height, slot_color, box_border_color],
        #     [right_column, top_row, slot_width, slot_height, slot_color, box_border_color],
        #     [left_column, bottom_row, slot_width, slot_height, slot_color, box_border_color],
        #     [middle_column, bottom_row, slot_width, slot_height, slot_color, box_border_color],
        #     [right_column, bottom_row, slot_width, slot_height, slot_color, box_border_color]
        # ]]

        # font = pygame.font.SysFont(None, 28)
        # y = self.screen.get_height() - 80
        # for opt in options:
        #     txt = font.render(opt, True, (255,255,255))
        #     self.screen.blit(txt, (40, y))
        #     y += 30
        

    # def draw_button(self, callback):

    def fade_sprite(self, char):
        found_sprite = next(sp for sp in self.enemy_sprites.sprites() + self.party_sprites.sprites() if sp.char_id == char.id)
        if found_sprite:
            found_sprite.set_target_alpha(100)
    
    def show_battle_menu(self):
        self.show_player_battle_menu = True
    
    def hide_battle_menu(self):
        self.show_player_battle_menu = False

    def update_player_positioning(self, player_x, player_y, player_angle):
        self.player_x = player_x
        self.player_y = player_y
        self.player_angle = player_angle

    def update_battle_ui(self, dt, time):
        for sprite in self.enemy_sprites.sprites():
            sprite.update(dt)
        for sprite in self.party_sprites.sprites():
            sprite.update(dt)
        if pygame.time.get_ticks() > self.last_message_ms + 2000:
            self.message_queue.clear()

    def render_dungeon_ui(self):
        self.draw_dungeon_geometry()
    
    def setup_battle_ui(self, enemies):
        self.create_sprites(self.game.party, enemies)
    
    def clear_messages(self):
        self.message_queue.clear()

    def add_to_message_queue(self, messages):
        self.clear_messages()
        if isinstance(messages, (str, int)):
            self.message_queue.append(messages)
        elif isinstance(messages, list):
            for message in messages:
                self.message_queue.append(message)
        else:
            self.message_queue.append('Failed to get message!')
        self.last_message_ms = pygame.time.get_ticks()
    
    def render_battle_ui(self):
        self.draw_battlefield()
        self.draw_sprites()
        if self.options and self.show_player_battle_menu == True:
            self.draw_player_menu()
        if self.game.party:
            self.draw_party_ui()
        if self.message_queue:
            self.draw_message_box(self.message_queue)
        