class ItemStack:
    def __init__(self, item, quantity=1):
        self.item     = item        
        self.quantity = quantity    

    def add(self, amount=1):
        self.quantity += amount

    def remove(self, amount=1):
        self.quantity = max(self.quantity - amount, 0)

    def is_empty(self):
        return self.quantity <= 0
    
    def activate(self, source, target, **kwargs):
        return self.item.activate(source, target, **kwargs)
    
    def __getattr__(self, name):
        """
        Called when an attribute lookup on the stack
        doesn’t find it on this object — forward it
        to self.item.
        """
        return getattr(self.item, name)

    def __repr__(self):
        return f"<{self.quantity}× {self.item.name}>"