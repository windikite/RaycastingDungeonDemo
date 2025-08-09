from character import Character

# Party Table
# Name - HP - ATT - RES - SPD - Player
party_table = [
    {
        "name": "Wyros",
        "max_health": 12,
        "cur_health": 12,
        "attack": 3,
        "resistance": 1,
        "speed": 2,
        "is_party": True,
        "inventory": [
            {"name":"Minor Potion of Healing", "quantity":3},
            {"name":"Silver Revolver", "quantity":1},
            {"name":"Revolver Ammo", "quantity":10},
        ],
        "magic": [
            "Stella",
            "Starshower"
        ],
        "sprite": "wyros"
    },
    {
        "name": "Sierra",
        "max_health": 12,
        "cur_health": 12,
        "attack": 3,
        "resistance": 1,
        "speed": 2,
        "is_party": True,
        "inventory": [
            {"name":"Minor Potion of Healing", "quantity":3},
            {"name":"Silver Revolver", "quantity":1},
            {"name":"Revolver Ammo", "quantity":10},
        ],
        "magic": [
            "Stella",
            "Starshower"
        ],
        "sprite": "sierra"
    },
    {
        "name": "Amy",
        "max_health": 12,
        "cur_health": 12,
        "attack": 3,
        "resistance": 1,
        "speed": 2,
        "is_party": True,
        "inventory": [
            {"name":"Minor Potion of Healing", "quantity":3},
            {"name":"Silver Revolver", "quantity":1},
            {"name":"Revolver Ammo", "quantity":10},
        ],
        "magic": [
            "Stella",
            "Starshower"
        ],
        "sprite": "amy"
    },
]

class SaveManager:
    def __init__(self, game, mag):
        self.game = game
        self.party = game.party
        self.mag = mag
        self.mag.subscribe("data:load", self.load_save)
    
    def generate_characters(self):
        self.party.clear()
        self.party.extend(Character(self.game, character_Data) for character_Data in party_table)

    def load_save(self):
        self.generate_characters()
