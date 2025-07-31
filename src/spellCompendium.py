from container import Container

class SpellCompendium(Container):
    def __init__(self, game, spell_records=[]):
        super().__init__()
        self.game = game
        self.load_spells(spell_records)
    
    def load_spells(self, spell_records):
        spell_map = {spell.name: spell for spell in self.game.magic}
        for spell_record in spell_records:
            name = spell_record

            spell = spell_map.get(name)
            if spell:
                self.add_spell(spell)

    def add_spell(self, spell):
        for x in self.slots:
            if x.name == spell:
                return
        self.slots.append(spell)

    def remove_spell(self, spell, qty=1):
        for x in self.slots:
            if x.id == spell.id:
                self.slots.remove(x)