import random, math
 
def RandomSelect(list_len, number, duplicate=False):
    if(list_len == 0): return []
    selected = []
    while len(selected) < number:
        index = random.randint(0, list_len - 1)
        if(index not in selected and duplicate == False):
            selected.append(index)
        elif(duplicate == True):
            selected.append(index)
    return selected
    
def find_item_id_by_name(items, name):
    for itm in items:
        if itm.get_name() == name:
            return itm.get_id()
    return None

