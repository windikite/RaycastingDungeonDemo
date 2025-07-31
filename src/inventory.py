from itemstack import ItemStack
from container import Container

class Inventory(Container):
    def __init__(self, game, item_records=[]):
        super().__init__()
        self.game = game
        self.load_items(item_records)
    
    def load_items(self, item_records):
        item_map = {itm.name: itm for itm in self.game.items}
        for item_record in item_records:
            name = item_record["name"]
            qty  = item_record["quantity"]

            item = item_map.get(name)
            if item:
                self.add_item(item, qty)

    def add_item(self, item, qty=1):
        for stack in self.slots:
            if stack.item.id == item.id:
                stack.add(qty)
                return
        self.slots.append(ItemStack(item, qty))

    def remove_item(self, item, qty=1):
        for stack in self.slots:
            if stack.item.id == item.id:
                stack.remove(qty)
                if stack.is_empty():
                    self.slots.remove(stack)
                return
    