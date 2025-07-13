import pygame
import math, random
from utils import *
from classes import *
from effects import *
from functools import partial

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 1920, 1080
RENDER_WIDTH, RENDER_HEIGHT = 320, 180
screen = pygame.display.set_mode((WIDTH, HEIGHT))
render_surface = pygame.Surface((RENDER_WIDTH, RENDER_HEIGHT))
pygame.display.set_caption("Raycasting Demo")

# Constants
FPS = 60
TILE_SIZE = 64
FOV = math.radians(60)
MAX_DEPTH = 800
player_x, player_y = 100.0, 100.0
player_angle = 0.0
move_speed = 100.0
rot_speed = 0.03
font = pygame.font.SysFont(None, 36)

# Smooth movement durations (seconds)
MOVE_DURATION = 0.25
TURN_DURATION = 0.25

# Map layout (1 = wall, 0 = empty)
dungeon = [
    [1]*26,
    [1]+[0]*24+[1],
    [1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,0,0,1],
    [1,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,1],
    [1,0,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0,0,1],
    [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,0,1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,0,1,1,0,1],
    [1,0,1,0,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,0,1,0,1,0,0,1],
    [1,0,1,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,0,1,1,1,0,0,1],
    [1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1]+[0]*24+[1],
    [1]*26,
]

clock = pygame.time.Clock()

# Movement/rotation state
moving = False
move_start_time = 0.0
move_start_pos = (player_x, player_y)
move_target_pos = (player_x, player_y)

turning = False
turn_start_time = 0.0
turn_start_angle = player_angle
turn_target_angle = player_angle

def draw_floor_and_ceiling(surface):
    mid = RENDER_HEIGHT // 2
    # Precompute ray directions at edges
    ray_x0 = math.cos(player_angle - FOV/2)
    ray_y0 = math.sin(player_angle - FOV/2)
    ray_x1 = math.cos(player_angle + FOV/2)
    ray_y1 = math.sin(player_angle + FOV/2)
    px, py = player_x / TILE_SIZE, player_y / TILE_SIZE

    for y in range(mid, RENDER_HEIGHT):
        p = y - mid
        if p == 0:
            continue
        row_dist = (TILE_SIZE * mid) / p
        step_x = row_dist * (ray_x1 - ray_x0) / RENDER_WIDTH
        step_y = row_dist * (ray_y1 - ray_y0) / RENDER_WIDTH
        floor_x = px + row_dist * ray_x0
        floor_y = py + row_dist * ray_y0

        brightness = max(0.1, min(1.0, 1 / (1 + row_dist * 0.01)))
        floor_color = tuple(int(c * brightness) for c in (41, 43, 48))
        ceil_color  = tuple(int(c * brightness) for c in (17, 20, 28))

        # Draw full scanline
        pygame.draw.line(surface, floor_color, (0, y), (RENDER_WIDTH, y))
        pygame.draw.line(surface, ceil_color,  (0, RENDER_HEIGHT - y - 1),
                         (RENDER_WIDTH, RENDER_HEIGHT - y - 1))

def cast_rays(surface, z_buffer, wall_bounds):
    for ray in range(RENDER_WIDTH):
        ray_angle = player_angle - FOV/2 + (ray / RENDER_WIDTH) * FOV
        cos_a = math.cos(ray_angle)
        sin_a = math.sin(ray_angle)

        map_x = int(player_x // TILE_SIZE)
        map_y = int(player_y // TILE_SIZE)

        delta_dist_x = abs(TILE_SIZE / (cos_a if cos_a != 0 else 1e-6))
        delta_dist_y = abs(TILE_SIZE / (sin_a if sin_a != 0 else 1e-6))

        if cos_a < 0:
            step_x = -1
            side_dist_x = (player_x - map_x * TILE_SIZE) / (abs(cos_a) if cos_a != 0 else 1e-6)
        else:
            step_x = 1
            side_dist_x = ((map_x + 1) * TILE_SIZE - player_x) / (abs(cos_a) if cos_a != 0 else 1e-6)

        if sin_a < 0:
            step_y = -1
            side_dist_y = (player_y - map_y * TILE_SIZE) / (abs(sin_a) if sin_a != 0 else 1e-6)
        else:
            step_y = 1
            side_dist_y = ((map_y + 1) * TILE_SIZE - player_y) / (abs(sin_a) if sin_a != 0 else 1e-6)

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

            if not (0 <= map_x < len(dungeon[0]) and 0 <= map_y < len(dungeon)):
                break
            if dungeon[map_y][map_x] == 1:
                break

        if side == 0:
            depth = side_dist_x - delta_dist_x
        else:
            depth = side_dist_y - delta_dist_y

        corrected_depth = depth * math.cos(ray_angle - player_angle)
        z_buffer[ray] = corrected_depth

        wall_height = (RENDER_HEIGHT * 60) / (corrected_depth + 0.0001)
        wall_top = max(0, int(RENDER_HEIGHT/2 - wall_height/2))
        wall_bottom = min(RENDER_HEIGHT, int(RENDER_HEIGHT/2 + wall_height/2))
        wall_bounds[ray] = (wall_top, wall_bottom)

        shade = max(0.2, 1 / (1 + corrected_depth * 0.01))
        color = tuple(int(c * shade) for c in (54, 62, 82))
        surface.fill(color, rect=(ray, wall_top, 1, wall_bottom - wall_top))

class Sprite:
    def __init__(self, world_x, world_y, height_offset=0.0, color=(255, 0, 0), size=8):
        self.world_x = world_x  # world coordinates in pixels
        self.world_y = world_y
        self.height_offset = height_offset  # from 0.0 (floor) to 1.0 (top of wall)
        self.color = color
        self.size = size

def draw_sprite(surface, sprite, z_buffer, wall_bounds):
    def normalize_angle(angle):
        return (angle + math.pi) % (2 * math.pi) - math.pi

    dx = sprite.world_x - player_x
    dy = sprite.world_y - player_y
    dist_to_obj = math.hypot(dx, dy)
    angle_to_obj = math.atan2(dy, dx)
    relative_angle = normalize_angle(angle_to_obj - player_angle)

    if abs(relative_angle) > FOV / 2:
        return

    screen_center_x = int(RENDER_WIDTH / 2 + (relative_angle / (FOV / 2)) * (RENDER_WIDTH / 2))
    proj_height = int(RENDER_HEIGHT * sprite.size * 60 / (dist_to_obj + 0.0001))
    sprite_half = proj_height // 2

    raw_top_y = int(RENDER_HEIGHT / 2 - sprite_half - sprite.height_offset * proj_height)
    raw_bottom_y = raw_top_y + proj_height

    for x in range(-sprite_half, sprite_half):
        screen_x = screen_center_x + x
        if not (0 <= screen_x < RENDER_WIDTH):
            continue

        wall_top, wall_bottom = wall_bounds[screen_x]
        wall_depth = z_buffer[screen_x]

        # Only draw sprite if it's closer than wall
        if dist_to_obj < wall_depth:
            # If the wall is closer, clip the sprite's visible vertical range
            top_y = max(raw_top_y, wall_top) if wall_depth < dist_to_obj else raw_top_y
            bottom_y = min(raw_bottom_y, wall_bottom) if wall_depth < dist_to_obj else raw_bottom_y

            if bottom_y > top_y:
                pygame.draw.line(surface, sprite.color, (screen_x, top_y), (screen_x, bottom_y))

# Sprites
sprites = [
    Sprite(3.5*TILE_SIZE, 1.5*TILE_SIZE, -0.5, (255,0,0), 1.0),
    Sprite(4.9*TILE_SIZE, 1.9*TILE_SIZE,  0.5, (0,255,0), 0.5),
    Sprite(3.5*TILE_SIZE, 3.5*TILE_SIZE,  1.0, (0,100,255), 0.75),
]

# Main loop
running = True
z_buffer = [float('inf')] * RENDER_WIDTH
wall_bounds = [(0, RENDER_HEIGHT)] * RENDER_WIDTH
encounter = False

# Party Table
# Name - HP - ATT - RES - SPD - Player
party_table = [
    ["Wynn", 12, 3, 1, 2, True],
    ["Rayne", 8, 4, 1, 4, True],
    ["Plat", 8, 4, 1, 4, True],
]

# Enemy Table
# Name - HP - ATT - RES - SPD - Player
enemy_table = [
    ["Goblin", 5, 3, 1, 3],
    ["Slime", 25, 2, 2, 0],
    ["Skeleton", 3, 2, 2, 1]
]

# Item Effects
minor_potion_effect = partial(Heal, amount=5)
medium_potion_effect = partial(Heal, amount=10)
major_potion_effect = partial(Heal, amount=20)


# Item Table
item_table = [
    ["Minor Potion of Healing", 50, "common", "A minor healing potion. Heals 5 health.", minor_potion_effect],
    ["Medium Potion of Healing", 150, "uncommon", "A medium healing potion. Heals 10 health.", medium_potion_effect],
    ["Major Potion of Healing", 450, "rare", "A major healing potion. Heals 20 health.", major_potion_effect],
    ["Revolver Ammo", 5, "rare", "Revolver ammo."],
]

game = Game()
ui = UI((WIDTH, HEIGHT))
game.enemy_templates = enemy_table

for x in party_table:
    game.create_character(*x)

for x in item_table:
    game.create_item(*x)

# Must wait to generate these effects as they depend on other items having an established ID
silver_revolver_effect = partial(Shoot_Revolver, ammo_id=find_item_id_by_name(game.items, "Revolver Ammo"), ammo_quantity=1, damage=8)

dependent_item_table = [
    ["Silver Revolver", 1500, "rare", "A silver revolver.", silver_revolver_effect],
]

for x in dependent_item_table:
    game.create_item(*x)

while running:
    dt = clock.tick(FPS) / 1000.0
    current_time = pygame.time.get_ticks() / 1000.0
    render_surface.fill((0,0,0))
    mouse_pos   = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]
    
    keys = pygame.key.get_pressed()

    in_battle = game.get_active_battle()

    # Initiate turning
    if not turning and not in_battle:
        if keys[pygame.K_LEFT]:
            turning = True
            turn_start_time   = current_time
            turn_start_angle  = player_angle
            turn_target_angle = player_angle - math.radians(90)
        elif keys[pygame.K_RIGHT]:
            turning = True
            turn_start_time   = current_time
            turn_start_angle  = player_angle
            turn_target_angle = player_angle + math.radians(90)

    # Initiate moving
    if not moving and not turning and not in_battle:
        if keys[pygame.K_UP]:
            tx = player_x + math.cos(player_angle)*TILE_SIZE
            ty = player_y + math.sin(player_angle)*TILE_SIZE
            if dungeon[int(ty/TILE_SIZE)][int(tx/TILE_SIZE)] == 0:
                moving = True
                move_start_time = current_time
                move_start_pos  = (player_x, player_y)
                move_target_pos = (tx, ty)
        elif keys[pygame.K_DOWN]:
            tx = player_x - math.cos(player_angle)*TILE_SIZE
            ty = player_y - math.sin(player_angle)*TILE_SIZE
            if dungeon[int(ty/TILE_SIZE)][int(tx/TILE_SIZE)] == 0:
                moving = True
                move_start_time = current_time
                move_start_pos  = (player_x, player_y)
                move_target_pos = (tx, ty)

    # Update turning interpolation
    if turning:
        t = (current_time - turn_start_time) / TURN_DURATION
        if t >= 1.0:
            player_angle = turn_target_angle
            turning = False
        else:
            player_angle = turn_start_angle + (turn_target_angle - turn_start_angle) * t

    # Update movement interpolation
    if moving:
        t = (current_time - move_start_time) / MOVE_DURATION
        if t >= 1.0:
            player_x, player_y = move_target_pos
            moving = False
            game.check_encounter(10)
        else:
            sx, sy = move_start_pos
            tx, ty = move_target_pos
            player_x = sx + (tx - sx) * t
            player_y = sy + (ty - sy) * t

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    draw_floor_and_ceiling(render_surface)
    z_buffer[:] = [float('inf')] * RENDER_WIDTH
    wall_bounds[:] = [(0, RENDER_HEIGHT)] * RENDER_WIDTH
    cast_rays(render_surface, z_buffer, wall_bounds)
    for spr in sprites:
        draw_sprite(render_surface, spr, z_buffer, wall_bounds)

    screen.blit(pygame.transform.scale(render_surface, (WIDTH, HEIGHT)), (0, 0))

    if not in_battle:
        party_clicked, items_clicked = ui.draw_dungeon_ui(
            surface     = screen,
            mouse_pos   = mouse_pos,
            mouse_click = mouse_click,
            font        = font,
            on_party    = lambda: print("Party button!"),
            on_items    = lambda: print("Items button!")
        )

    if in_battle:
        ui.draw_combat_bar(
            surface     = screen,
            mouse_pos   = mouse_pos,
            mouse_click = mouse_click,
            font        = font,
            callback    = game.clear_battle
        )

    pygame.display.flip()

pygame.quit()
