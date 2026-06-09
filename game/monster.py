# Monster Definitions
import random

class Monster:

    def __init__(self, template):
        self.name = template['name']
        self.max_hp = template['hp']
        self.hp = self.max_hp
        self.atk = template['atk']
        self.defense = template['def']
        self.mag = template.get('mag', 5)
        self.spd = template['spd']
        self.exp_reward = template['exp']
        self.gold_reward = template['gold']
        self.color = tuple(template['color'])
        self.size = template.get('size', 'medium')
        self.is_boss = template.get('boss', False)
        self.alive = True
        self.skills = template.get('skills', [])
        self.weakness = template.get('weakness', None)
        self.sprite_type = template.get('sprite', 'slime')

    def take_damage(self, damage, element=None):
        actual_damage = damage
        if element and self.weakness == element:
            actual_damage = int(damage * 1.5)  # Weak = 1.5x damage
        actual = min(self.hp, max(1, actual_damage))
        self.hp -= actual
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return actual

    def choose_action(self, heroes):
        alive_heroes = [h for h in heroes if h.alive]
        if not alive_heroes:
            return None

        # Boss punya chance lebih besar pakai skill
        if self.skills and random.random() < (0.4 if self.is_boss else 0.25):
            skill = random.choice(self.skills)
            if skill.get('target') == 'all':
                return {'type': 'skill', 'skill': skill, 'targets': alive_heroes}
            else:
                target = random.choice(alive_heroes)
                return {'type': 'skill', 'skill': skill, 'targets': [target]}

        # Default: attack random hero (prefer low HP targets)
        alive_heroes.sort(key=lambda h: h.hp)
        if random.random() < 0.6:
            target = alive_heroes[0]  # target lowest HP
        else:
            target = random.choice(alive_heroes)

        return {'type': 'attack', 'targets': [target]}

    def use_mp(self, cost):
        return True

    def heal(self, amount):
        actual = min(self.max_hp - self.hp, amount)
        self.hp += actual
        if self.hp > 0:
            self.alive = True
        return actual

    def restore_mp(self, amount):
        pass

    @property
    def hp_ratio(self):
        return self.hp / self.max_hp if self.max_hp > 0 else 0

MONSTER_TEMPLATES = {
    'slime': {
        'name': 'Slime',
        'hp': 30, 'atk': 8, 'def': 4, 'mag': 3, 'spd': 6,
        'exp': 12, 'gold': 8,
        'color': [80, 200, 80],
        'size': 'small',
        'sprite': 'slime',
        'weakness': 'fire',
    },
    'goblin': {
        'name': 'Goblin',
        'hp': 50, 'atk': 14, 'def': 8, 'mag': 4, 'spd': 10,
        'exp': 20, 'gold': 15,
        'color': [100, 160, 60],
        'size': 'medium',
        'sprite': 'goblin',
        'weakness': 'ice',
        'skills': [
            {'name': 'Slash', 'power': 1.3, 'type': 'physical', 'element': 'none', 'target': 'single'},
        ],
    },
    'skeleton': {
        'name': 'Skeleton',
        'hp': 65, 'atk': 16, 'def': 6, 'mag': 8, 'spd': 8,
        'exp': 28, 'gold': 20,
        'color': [220, 220, 200],
        'size': 'medium',
        'sprite': 'skeleton',
        'weakness': 'heal',
        'skills': [
            {'name': 'Bone Throw', 'power': 1.5, 'type': 'physical', 'element': 'none', 'target': 'single'},
        ],
    },
    'dark_knight': {
        'name': 'Dark Knight',
        'hp': 100, 'atk': 22, 'def': 16, 'mag': 12, 'spd': 9,
        'exp': 45, 'gold': 35,
        'color': [60, 40, 80],
        'size': 'large',
        'sprite': 'knight',
        'weakness': 'thunder',
        'skills': [
            {'name': 'Dark Slash', 'power': 1.8, 'type': 'physical', 'element': 'dark', 'target': 'single'},
            {'name': 'Shadow Wave', 'power': 1.3, 'type': 'magic', 'element': 'dark', 'target': 'all'},
        ],
    },
    'dragon': {
        'name': 'Crystal Dragon',
        'hp': 300, 'atk': 30, 'def': 20, 'mag': 25, 'spd': 12,
        'exp': 200, 'gold': 150,
        'color': [180, 50, 50],
        'size': 'boss',
        'sprite': 'dragon',
        'boss': True,
        'weakness': 'ice',
        'skills': [
            {'name': 'Fire Breath', 'power': 2.0, 'type': 'magic', 'element': 'fire', 'target': 'all'},
            {'name': 'Tail Whip', 'power': 2.2, 'type': 'physical', 'element': 'none', 'target': 'single'},
            {'name': 'Crystal Storm', 'power': 2.5, 'type': 'magic', 'element': 'ice', 'target': 'all'},
        ],
    },
}

def create_monster(monster_type):
    template = MONSTER_TEMPLATES.get(monster_type)
    if template:
        return Monster(template)
    return Monster(MONSTER_TEMPLATES['slime'])

def get_random_encounter(map_type='dungeon', floor=1):
    encounters = {
        'dungeon': {
            1: [['slime'], ['slime', 'slime'], ['goblin']],
            2: [['goblin', 'slime'], ['skeleton'], ['goblin', 'goblin']],
            3: [['skeleton', 'goblin'], ['dark_knight'], ['skeleton', 'skeleton']],
        },
    }
    map_enc = encounters.get(map_type, encounters['dungeon'])
    floor_enc = map_enc.get(min(floor, max(map_enc.keys())), map_enc[1])
    chosen = random.choice(floor_enc)
    return [create_monster(m) for m in chosen]
