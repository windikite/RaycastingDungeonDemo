from functools import partial
import random

def Heal(source, target, amount):
    print('attempting to heal')
    t1 = source.get_name()
    t2 = target.get_name()
    health = target.set_hp(amount)
    return f'{t1} healed {t2} for {amount} health! {t2} now has {health} health.'
    
def Damage(source, target, amount):
    health = target.take_damage(amount)
    return health

def Stella(source, target):
    damage_amount = random.randint(7, 13)
    return Damage(source, target, damage_amount)

def Starshower(source, defenders):
    print(f'{source.get_name()} calls down a shower of stars!')
    for x in defenders:
        damage_amount = random.randint(1, 3)
        Damage(source, x, damage_amount)

def Projectile_Weapon_With_Ammo(source, target, ammo_id, ammo_quantity, damage):
    stack = next(
        (s for s in source.inventory.slots if s.item.id == ammo_id),
        None
    )
    
    if stack is None:
        print(f"{source.get_name()} has no ammo (id={ammo_id})!")
        return False

    if stack.quantity < ammo_quantity:
        print(f"{source.get_name()} only has {stack.quantity} ammo, needs {ammo_quantity}.")
        return False

    stack.remove(ammo_quantity)
    if stack.is_empty():
        source.inventory.slots.remove(stack)

    Damage(source, target, damage)
    return True

def Shoot_Revolver(source, target, ammo_id, ammo_quantity, damage):
    print(f'{source.get_name()} tries to shoot {target.get_name()} with a revolver!')
    shot = Projectile_Weapon_With_Ammo(source, target, ammo_id, ammo_quantity, damage)

def AOEDamage(source, targets, damage_amount):
    for target in targets:
        Damage(source, target, damage_amount)
    return True

def Weapon_Attack(source, target):
    attack_message, current_health, damage_message = source.attack(target)
    return attack_message, current_health, damage_message