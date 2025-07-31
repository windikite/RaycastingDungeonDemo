from action import Action

class Spell(Action):
    def __init__(self, spell_data):
        super().__init__(spell_data["name"], spell_data["action_type"], spell_data["callback"], spell_data["target_style"], spell_data["can_target"])
        self.description = spell_data["description"]
        self.mana_cost = spell_data["mana_cost"]
        self.level = spell_data["level"]
    
    def get_description(self):
        return self.description


