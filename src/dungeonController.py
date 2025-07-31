import pygame, math, random
from utils import *
from battleController import BattleController
from character import Character

# Name - HP - ATT - RES - SPD - Player
enemy_table = [
    {
        "name": "Goblin",
        "max_health": 5,
        "cur_health": 5,
        "attack": 3,
        "resistance": 1,
        "speed": 3,
        "is_party": False,
        "inventory": [
        ],
        "magic": [
        ],
        "sprite": "goblin"
    },
    {
        "name": "Slime",
        "max_health": 15,
        "cur_health": 15,
        "attack": 2,
        "resistance": 2,
        "speed": 0,
        "is_party": False,
        "inventory": [
        ],
        "magic": [
        ],
        "sprite": "slime"
    },
    {
        "name": "Skeleton",
        "max_health": 3,
        "cur_health": 3,
        "attack": 2,
        "resistance": 2,
        "speed": 1,
        "is_party": False,
        "inventory": [
        ],
        "magic": [
        ],
        "sprite": "skeleton"
    },
]

class DungeonController:
    def __init__(self, game, dungeon_map):
        self.game = game
        self.dungeon_map = dungeon_map
        self.dungeon_start_cell = (1, 1)
        self.enemy_templates = enemy_table#should be loaded later from game data
        self.TILE_SIZE = 64
        self.RENDER_WIDTH, self.RENDER_HEIGHT = 320, 180
        self.render_surface = pygame.Surface((self.RENDER_WIDTH, self.RENDER_HEIGHT))
        self.player_x, self.player_y, self.player_angle = (self.dungeon_start_cell[0] + 0.5) * self.TILE_SIZE, (self.dungeon_start_cell[1] + 0.5) * self.TILE_SIZE, 0.0
        self.moving = self.turning = False
        self.move_t0 = self.turn_t0 = 0
        self.start_pos = self.target_pos = (self.player_x, self.player_y)
        self.start_ang = self.target_ang = self.player_angle

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and not (self.moving or self.turning):
                now = pygame.time.get_ticks()/1000
                if e.key == pygame.K_LEFT:
                    self.turning = True
                    self.turn_t0 = now
                    self.start_ang = self.player_angle
                    self.target_ang= self.player_angle - math.radians(90)
                if e.key == pygame.K_RIGHT:
                    self.turning = True
                    self.turn_t0 = now
                    self.start_ang = self.player_angle
                    self.target_ang= self.player_angle + math.radians(90)
                if e.key == pygame.K_UP:
                    tx = self.player_x + math.cos(self.player_angle)*self.TILE_SIZE
                    ty = self.player_y + math.sin(self.player_angle)*self.TILE_SIZE
                    if self.dungeon_map[int(ty/self.TILE_SIZE)][int(tx/self.TILE_SIZE)]==0:
                        self.moving = True
                        self.move_t0 = now
                        self.start_pos = (self.player_x,self.player_y)
                        self.target_pos= (tx,ty)
                if e.key == pygame.K_DOWN:
                    tx = self.player_x - math.cos(self.player_angle)*self.TILE_SIZE
                    ty = self.player_y - math.sin(self.player_angle)*self.TILE_SIZE
                    if self.dungeon_map[int(ty/self.TILE_SIZE)][int(tx/self.TILE_SIZE)]==0:
                        self.moving = True
                        self.move_t0 = now
                        self.start_pos = (self.player_x,self.player_y)
                        self.target_pos= (tx,ty)
    
    def update(self):
        now = pygame.time.get_ticks()/1000
        if self.turning:
            t = (now-self.turn_t0)/0.25
            if t>=1:
                self.player_angle, self.turning = self.target_ang, False
            else:
                self.player_angle = self.start_ang + (self.target_ang-self.start_ang)*t
        if self.moving:
            t = (now-self.move_t0)/0.25
            if t>=1:
                self.player_x, self.player_y = self.target_pos
                self.moving = False
                self.check_encounter(100)
            else:
                sx,sy = self.start_pos
                tx,ty = self.target_pos
                self.player_x = sx + (tx-sx)*t
                self.player_y = sy + (ty-sy)*t
    
    def render(self):
        self.game.UI.draw_dungeon_geometry()
        # self.ui.draw_dungeon_ui(
        #     surface     = self.screen,
        #     mouse_pos   = pygame.mouse.get_pos(),
        #     mouse_click = pygame.mouse.get_pressed()[0],
        #     font        = pygame.font.SysFont(None,36),
        #     callback_1  = lambda: None
        # )
    
    def create_battle(self):
        new_battle = BattleController(self.game, self.game.party, self.generate_encounter())
        self.game.battle = new_battle
        self.game.state = "BATTLE"
        # self.game.battle.start_battle()
    
    def generate_encounter(self):
        selected_enemy_indices = RandomSelect(len(self.enemy_templates), 3, True)
        selected_enemies = [Character(self.game, self.enemy_templates[x]) for x in selected_enemy_indices]
        return selected_enemies
    
    def check_encounter(self, chance):
        is_encounter = True if (random.randint(1, 100) > (100 - chance)) else False
        if(is_encounter):
            self.create_battle()
        return is_encounter

    
    