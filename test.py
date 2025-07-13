from utils import *
from classes import *
from effects import *
from functools import partial

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
    
game.enemy_templates = enemy_table
game.create_battle()
game.items[0].activate(game.party[0], game.party[1])
game.items[2].activate(game.party[2], game.party[0])
game.items[1].activate(game.party[1], game.party[2])
game.party[0].inventory.add_item(game.items[3], 5)
game.items[4].activate(game.party[0], game.party[1])