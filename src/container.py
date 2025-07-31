class Container:
    def __init__(self):
        self.slots = []

    
    def get_items(self):
        print('slots', self.slots)
        return self.slots

    def __repr__(self):
        return ", ".join(str(s) for s in self.slots)