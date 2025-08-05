import pygame, math, random
from utils import *
from battleController import BattleController
from character import Character

class DungeonController:
    def __init__(self, game, dungeon_map, mag):
        self.game = game
        self.dungeon_map = dungeon_map
        self.mag = mag
        self.dungeon_start_cell = (1, 1)
        self.enemy_templates = self.game.enemy_templates
        self.TILE_SIZE = 64
        self.RENDER_WIDTH, self.RENDER_HEIGHT = 320, 180
        self.render_surface = pygame.Surface((self.RENDER_WIDTH, self.RENDER_HEIGHT))
        self.player_x, self.player_y, self.player_angle = (self.dungeon_start_cell[0] + 0.5) * self.TILE_SIZE, (self.dungeon_start_cell[1] + 0.5) * self.TILE_SIZE, 0.0
        self.moving = self.turning = False
        self.move_t0 = self.turn_t0 = 0
        self.start_pos = self.target_pos = (self.player_x, self.player_y)
        self.start_ang = self.target_ang = self.player_angle

        self.mag.subscribe("explore:input", self.handle_event)
        self.mag.subscribe("explore:update", self.update)
        self.mag.subscribe("explore:render", self.render)

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
    
    def update(self, dt, time):
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
        self.mag.publish("player:position", player_x=self.player_x, player_y=self.player_y, player_angle=self.player_angle)
    
    def render(self):
        self.mag.publish("dungeon:render")
    
    def check_encounter(self, chance):
        is_encounter = True if (random.randint(1, 100) > (100 - chance)) else False
        if(is_encounter):
            self.mag.publish("battle:start")
            self.mag.publish("state:change")
        return is_encounter

    
    