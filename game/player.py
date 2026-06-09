"""
game/player.py - Player & Party System
========================================
Definisi karakter hero dan party management.
"""

import math
import json
import os

SAVE_FILE = 'savegame.json'


class Character:
    """Satu karakter hero dalam party."""

    def __init__(self, name, char_class, level=1):
        self.name = name
        self.char_class = char_class  # 'warrior', 'mage', 'healer'
        self.level = level

        # Base stats tergantung class
        base_stats = {
            'warrior': {'hp': 120, 'mp': 20,  'atk': 18, 'def': 14, 'mag': 5,  'spd': 10, 'color': (200, 60, 60)},
            'mage':    {'hp': 70,  'mp': 60,  'atk': 8,  'def': 8,  'mag': 20, 'spd': 12, 'color': (120, 60, 200)},
            'healer':  {'hp': 90,  'mp': 45,  'atk': 10, 'def': 10, 'mag': 16, 'spd': 11, 'color': (60, 180, 100)},
        }
        stats = base_stats.get(char_class, base_stats['warrior'])

        # Stats scaled by level
        scale = 1 + (level - 1) * 0.15
        self.max_hp = int(stats['hp'] * scale)
        self.max_mp = int(stats['mp'] * scale)
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.atk = int(stats['atk'] * scale)
        self.defense = int(stats['def'] * scale)
        self.mag = int(stats['mag'] * scale)
        self.spd = int(stats['spd'] * scale)
        self.color = stats['color']

        # Experience
        self.exp = 0
        self.exp_to_next = self._calc_exp_needed()

        # Status
        self.alive = True
        self.defending = False

        # Spells berdasarkan class
        self.spells = self._get_spells()

    def _calc_exp_needed(self):
        return int(50 * (self.level ** 1.5))

    def _get_spells(self):
        spells = {
            'warrior': [
                {'name': 'Power Slash', 'mp_cost': 8, 'power': 1.8, 'type': 'physical', 'element': 'none', 'target': 'single'},
            ],
            'mage': [
                {'name': 'Fire', 'mp_cost': 8, 'power': 2.0, 'type': 'magic', 'element': 'fire', 'target': 'single'},
                {'name': 'Ice', 'mp_cost': 8, 'power': 2.0, 'type': 'magic', 'element': 'ice', 'target': 'single'},
                {'name': 'Thunder', 'mp_cost': 12, 'power': 2.5, 'type': 'magic', 'element': 'thunder', 'target': 'all'},
            ],
            'healer': [
                {'name': 'Heal', 'mp_cost': 6, 'power': 2.0, 'type': 'heal', 'element': 'heal', 'target': 'single'},
                {'name': 'Barrier', 'mp_cost': 10, 'power': 0, 'type': 'buff', 'element': 'none', 'target': 'single'},
                {'name': 'Holy', 'mp_cost': 15, 'power': 2.2, 'type': 'magic', 'element': 'heal', 'target': 'single'},
            ],
        }
        return spells.get(self.char_class, [])

    def take_damage(self, damage, element=None):
        """Terima damage, return actual damage dealt."""
        if self.defending:
            damage = damage // 2
        actual = min(self.hp, max(1, damage))
        self.hp -= actual
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return actual

    def heal(self, amount):
        """Heal HP."""
        actual = min(self.max_hp - self.hp, amount)
        self.hp += actual
        if self.hp > 0:
            self.alive = True
        return actual

    def use_mp(self, cost):
        """Use MP, return True if sufficient."""
        if self.mp >= cost:
            self.mp -= cost
            return True
        return False

    def restore_mp(self, amount):
        """Restore MP."""
        self.mp = min(self.max_mp, self.mp + amount)

    def gain_exp(self, amount):
        """Gain EXP, return True if leveled up."""
        self.exp += amount
        if self.exp >= self.exp_to_next:
            self.level_up()
            return True
        return False

    def level_up(self):
        """Level up! Increase stats."""
        self.level += 1
        self.exp -= self.exp_to_next
        self.exp_to_next = self._calc_exp_needed()

        # Stat growth
        growth = {
            'warrior': {'hp': 15, 'mp': 3,  'atk': 3, 'def': 2, 'mag': 1, 'spd': 1},
            'mage':    {'hp': 8,  'mp': 8,  'atk': 1, 'def': 1, 'mag': 3, 'spd': 1},
            'healer':  {'hp': 10, 'mp': 6,  'atk': 1, 'def': 2, 'mag': 2, 'spd': 1},
        }
        g = growth.get(self.char_class, growth['warrior'])

        self.max_hp += g['hp']
        self.max_mp += g['mp']
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.atk += g['atk']
        self.defense += g['def']
        self.mag += g['mag']
        self.spd += g['spd']

        # Unlock new spells at certain levels
        new_spells = {
            'warrior': {3: {'name': 'Berserk', 'mp_cost': 12, 'power': 2.5, 'type': 'physical', 'element': 'none', 'target': 'single'}},
            'mage':    {3: {'name': 'Meteor', 'mp_cost': 25, 'power': 3.5, 'type': 'magic', 'element': 'fire', 'target': 'all'}},
            'healer':  {3: {'name': 'Revive', 'mp_cost': 20, 'power': 0.5, 'type': 'revive', 'element': 'heal', 'target': 'single'}},
        }
        class_spells = new_spells.get(self.char_class, {})
        if self.level in class_spells:
            self.spells.append(class_spells[self.level])

    def full_restore(self):
        """Full restore HP/MP."""
        self.hp = self.max_hp
        self.mp = self.max_mp
        self.alive = True
        self.defending = False

    @property
    def hp_ratio(self):
        return self.hp / self.max_hp if self.max_hp > 0 else 0

    @property
    def mp_ratio(self):
        return self.mp / self.max_mp if self.max_mp > 0 else 0

    def to_dict(self):
        return {
            'name': self.name,
            'char_class': self.char_class,
            'level': self.level,
            'max_hp': self.max_hp,
            'max_mp': self.max_mp,
            'hp': self.hp,
            'mp': self.mp,
            'atk': self.atk,
            'defense': self.defense,
            'mag': self.mag,
            'spd': self.spd,
            'color': self.color,
            'exp': self.exp,
            'exp_to_next': self.exp_to_next,
            'alive': self.alive,
            'spells': self.spells
        }

    @classmethod
    def from_dict(cls, data):
        c = cls(data['name'], data['char_class'], data['level'])
        c.max_hp = data['max_hp']
        c.max_mp = data['max_mp']
        c.hp = data['hp']
        c.mp = data['mp']
        c.atk = data['atk']
        c.defense = data['defense']
        c.mag = data['mag']
        c.spd = data['spd']
        c.color = tuple(data['color'])
        c.exp = data['exp']
        c.exp_to_next = data['exp_to_next']
        c.alive = data['alive']
        c.spells = data['spells']
        return c


class Party:
    """Party of heroes."""

    def __init__(self):
        self.members = []
        self.gold = 100
        self.inventory = []
        self.position = [5, 5]  # posisi di peta
        self.direction = 'down'
        self.current_map = 'town'

    def add_member(self, character):
        self.members.append(character)

    def get_alive_members(self):
        return [m for m in self.members if m.alive]

    def is_wiped(self):
        return len(self.get_alive_members()) == 0

    def full_restore(self):
        for m in self.members:
            m.full_restore()

    @staticmethod
    def create_default_party():
        """Buat party default dengan 3 hero."""
        party = Party()
        party.add_member(Character("Aric", "warrior", 1))
        party.add_member(Character("Luna", "mage", 1))
        party.add_member(Character("Sage", "healer", 1))

        # Starting items
        party.inventory = [
            {'name': 'Potion', 'type': 'heal_hp', 'power': 50, 'count': 5},
            {'name': 'Ether', 'type': 'heal_mp', 'power': 30, 'count': 3},
            {'name': 'Phoenix Down', 'type': 'revive', 'power': 0.3, 'count': 1},
        ]
        return party

    def save_to_file(self):
        data = {
            'members': [m.to_dict() for m in self.members],
            'gold': self.gold,
            'inventory': self.inventory,
            'position': self.position,
            'direction': self.direction,
            'current_map': self.current_map
        }
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)
            
    @staticmethod
    def load_from_file():
        if not os.path.exists(SAVE_FILE):
            return None
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
            party = Party()
            party.members = [Character.from_dict(m) for m in data['members']]
            party.gold = data['gold']
            party.inventory = data['inventory']
            party.position = data['position']
            party.direction = data['direction']
            party.current_map = data['current_map']
            return party
        except Exception:
            return None
