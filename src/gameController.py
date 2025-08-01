import pygame
from dungeonController import DungeonController
from saveManager import SaveManager
from uiController import UI
from utils import *
from effects import *
from item import Item
from spell import Spell

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
        self.state  = "EXPLORE"
        self.battle = None
        self.party = []
        self.items = []
        self.magic = []
        self.save_manager = SaveManager(self)
        self.dungeon_controller = DungeonController(self, dungeon_map)
        self.UI = UI(self)

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
        
        self.save_manager.load_save()
    
    def handle_event(self, e):
        if e.type == pygame.QUIT:
            self.running = False
        elif self.state == "BATTLE":
            self.battle.handle_event(e)
        else:
            self.dungeon_controller.handle_event(e)
            
    
    def update(self, dt):
        if self.state == "BATTLE":
            self.battle.update(dt)
        else:
            self.dungeon_controller.update()
    
    def render(self):
        if self.state == "BATTLE":
            self.battle.render()
        else:
            self.dungeon_controller.render()
    
    def run(self):
        self.running = True
        while self.running:
            self.dt = self.clock.tick(self.FPS)/1000
            for e in pygame.event.get():
                self.handle_event(e)
            self.update(self.dt)
            self.render()
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    GameController().run()
