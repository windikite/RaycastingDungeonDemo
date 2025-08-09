class Turn:
    def __init__(self, character, action, target):
        self.character = character 
        self.action = action
        self.target = target
    
    def resolve_turn(self):
        result = self.action.activate(self.character, self.target)
        self.character.set_cooldown(10000)
        return result