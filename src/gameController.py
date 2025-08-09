import pygame
from dungeonController import DungeonController
from battleController import BattleController
from saveManager import SaveManager
from uiController import UI
from magazine import Mag
from utils import *
from effects import *
from item import Item
from spell import Spell
from actionMenu import ActionMenu

dungeon_map = [
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

# Name - HP - ATT - RES - SPD - Player
enemy_table = [
    # {
    #     "name": "Goblin",
    #     "max_health": 5,
    #     "cur_health": 5,
    #     "attack": 3,
    #     "resistance": 1,
    #     "speed": 3,
    #     "is_party": False,
    #     "inventory": [
    #     ],
    #     "magic": [
    #     ],
    #     "sprite": "goblin"
    # },
    # {
    #     "name": "Slime",
    #     "max_health": 15,
    #     "cur_health": 15,
    #     "attack": 2,
    #     "resistance": 2,
    #     "speed": 0,
    #     "is_party": False,
    #     "inventory": [
    #     ],
    #     "magic": [
    #     ],
    #     "sprite": "slime"
    # },
    # {
    #     "name": "Skeleton",
    #     "max_health": 3,
    #     "cur_health": 3,
    #     "attack": 2,
    #     "resistance": 2,
    #     "speed": 1,
    #     "is_party": False,
    #     "inventory": [
    #     ],
    #     "magic": [
    #     ],
    #     "sprite": "skeleton"
    # },
    {
        "name": "Snix",
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
        "sprite": "snix"
    },
    {
        "name": "Snox",
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
        "sprite": "snox"
    },
    {
        "name": "Snax",
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
        "sprite": "snax"
    },
]

# Item Effects
minor_potion_effect = partial(Heal, amount=5)
medium_potion_effect = partial(Heal, amount=10)
major_potion_effect = partial(Heal, amount=20)

# Item Table
item_table = [
    {
        "name": "Minor Potion of Healing",
        "value": 50,
        "rarity": "Common",
        "description": "A minor healing potion. Heals 5 health.",
        "action_type": "Consumable",
        "callback": minor_potion_effect,
        "target_style": "Single",
        "can_target": "Party"
    },
    {
        "name": "Medium Potion of Healing",
        "value": 150,
        "rarity": "Uncommon",
        "description": "A medium healing potion. Heals 10 health.",
        "action_type": "Consumable",
        "callback": medium_potion_effect,
        "target_style": "Single",
        "can_target": "Party"
    },
    {
        "name": "Major Potion of Healing",
        "value": 450,
        "rarity": "Rare",
        "description": "A major healing potion. Heals 20 health.",
        "action_type": "Consumable",
        "callback": major_potion_effect,
        "target_style": "Single",
        "can_target": "Party"
    },
    {
        "name": "Revolver Ammo",
        "value": 5,
        "rarity": "Rare",
        "description": "Revolver ammo.",
        "action_type": "Ammo",
        "callback": None,
        "target_style": None,
        "can_target": None
    },
]

spell_table = [
    {
        "name": "Stella",
        "description": "A beam of light from the constellations above.",
        "action_type": "Spell",
        "callback": Stella,
        "target_style": "Single",
        "can_target": "Enemies",
        "mana_cost": 10,
        "level": 1
    },
    {
        "name": "Starshower",
        "description": "Revolver ammo.",
        "action_type": "Spell",
        "callback": Starshower,
        "target_style": "All",
        "can_target": "Enemies",
        "mana_cost": 10,
        "level": 1
    },
]

class GameController:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("SMT")
        self.clock  = pygame.time.Clock()
        self.FPS = 60
        self.state  = "explore"
        self.mag = Mag()
        self.party = []
        self.items = []
        self.magic = []
        self.enemies = []
        self.enemy_templates = enemy_table
        self.battle = BattleController(self, self.mag)
        self.save_manager = SaveManager(self, self.mag)
        self.dungeon_controller = DungeonController(self, dungeon_map, self.mag)
        self.action_menu = ActionMenu(self, self.mag)
        self.UI = UI(self, self.mag)

        self.mag.subscribe("state:change", self.change_state)

        for x in item_table:
            self.items.append(Item(x))
        
        for x in spell_table:
            self.magic.append(Spell(x))

        # Must wait to generate these effects as they depend on other items having an established ID
        silver_revolver_effect = partial(Shoot_Revolver, ammo_id=find_item_id_by_name(self.items, "Revolver Ammo"), ammo_quantity=1, damage=8)

        dependent_item_table = [
            {
                "name": "Silver Revolver",
                "value": 1500,
                "rarity": "Rare",
                "description": "A silver revolver.",
                "action_type": "Ammo",
                "callback": silver_revolver_effect,
                "target_style": "Single",
                "can_target": "Enemies"
            },
        ]
        for x in dependent_item_table:
            self.items.append(Item(x))
        
        self.mag.publish("data:load")
    
    def change_state(self):
        if self.state == "explore":
            self.state = "battle"
        elif self.state == "battle":
            self.state = "explore"
    
    def run(self):
        self.running = True
        while self.running:
            self.dt = self.clock.tick(self.FPS)/1000
            self.time = pygame.time.get_ticks()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                self.mag.publish(f"{self.state}:input", e=e)
            self.mag.publish(f"{self.state}:update", dt=self.dt, time=self.time)
            self.mag.publish(f"{self.state}:render")
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    GameController().run()
