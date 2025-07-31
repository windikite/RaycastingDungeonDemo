from entity import Entity

class Action(Entity):
    def __init__(self, name, action_type, callback, target_style="Single", can_target="Enemies"):
        super().__init__(name)
        self.callback = callback
        self.type = action_type
        self.target_style = target_style
        self.can_target = can_target

    def activate(self, source, target, **kwargs):
        return self.callback(source, target, **kwargs)
    
