class Entity:
    registry = []
    _global_id = 0

    def __init__(self, name):
        self.id   = Entity._global_id
        Entity._global_id += 1
        self.name = name
        Entity.registry.append(self)
        
    def get_id(self):
        return self.id
        
    def get_name(self):
        return self.name