from action import Action

class Item(Action):
    def __init__(self, item_data):
        super().__init__(item_data["name"], item_data["action_type"], item_data["callback"], item_data["target_style"], item_data["can_target"])
        self.value = item_data["value"]
        self.rarity = item_data["rarity"]
        self.description = item_data["description"]
    
    def get_value(self):
        return self.value
    
    def get_rarity(self):
        return self.rarity
    
    def get_description(self):
        return self.description


