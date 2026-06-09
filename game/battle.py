# Turn-Based Battle System
import random
import math

class BattleState:
    START = 'start'
    PLAYER_TURN = 'player_turn'
    CHOOSE_ACTION = 'choose_action'
    CHOOSE_TARGET = 'choose_target'
    CHOOSE_SPELL = 'choose_spell'
    CHOOSE_ITEM = 'choose_item'
    EXECUTE_ACTION = 'execute_action'
    ENEMY_TURN = 'enemy_turn'
    VICTORY = 'victory'
    DEFEAT = 'defeat'
    FLEE = 'flee'
    ANIMATION = 'animation'

class BattleAction:
    def __init__(self, action_type, actor, targets=None, spell=None, item=None):
        self.type = action_type  # 'attack', 'magic', 'item', 'defend', 'flee'
        self.actor = actor
        self.targets = targets or []
        self.spell = spell
        self.item = item
        self.results = []

class BattleSystem:

    def __init__(self, party, monsters):
        self.party = party
        self.monsters = monsters
        self.state = BattleState.START

        # Turn order berdasarkan speed
        self.turn_order = []
        self.current_turn_index = 0
        self.current_actor = None

        # Player menu
        self.menu_index = 0
        self.target_index = 0
        self.spell_index = 0
        self.item_index = 0

        # Results
        self.action_queue = []
        self.current_action = None
        self.animation_timer = 0
        self.battle_log = []

        # Victory data
        self.total_exp = 0
        self.total_gold = 0
        self.leveled_up = []

        # Can flee?
        self.can_flee = not any(m.is_boss for m in monsters)

        # Init turn order
        self._calculate_turn_order()

    def _calculate_turn_order(self):
        combatants = []
        for m in self.party.get_alive_members():
            combatants.append(('hero', m))
        for m in self.monsters:
            if m.alive:
                combatants.append(('monster', m))

        combatants.sort(key=lambda c: c[1].spd, reverse=True)
        self.turn_order = combatants
        self.current_turn_index = 0

    def get_current_actor(self):
        if self.current_turn_index < len(self.turn_order):
            return self.turn_order[self.current_turn_index]
        return None

    def next_turn(self):
        self.current_turn_index += 1

        # Cek apakah semua sudah mendapat giliran
        if self.current_turn_index >= len(self.turn_order):
            # Reset turn order
            self._calculate_turn_order()

        # Skip dead combatants
        while self.current_turn_index < len(self.turn_order):
            actor_type, actor = self.turn_order[self.current_turn_index]
            if actor.alive:
                break
            self.current_turn_index += 1

        if self.current_turn_index >= len(self.turn_order):
            self._calculate_turn_order()

        # Check win/lose
        if all(not m.alive for m in self.monsters):
            self.state = BattleState.VICTORY
            self._calculate_rewards()
            return
        if self.party.is_wiped():
            self.state = BattleState.DEFEAT
            return

        # Set state berdasarkan actor type
        actor_type, actor = self.get_current_actor()
        actor.defending = False
        if actor_type == 'hero':
            self.state = BattleState.CHOOSE_ACTION
            self.menu_index = 0
        else:
            self.state = BattleState.ENEMY_TURN

    def execute_attack(self, attacker, target):
        base_damage = attacker.atk * 2 - target.defense
        variance = random.uniform(0.85, 1.15)
        damage = max(1, int(base_damage * variance))
        critical = random.random() < 0.1
        if critical:
            damage = int(damage * 1.5)
        actual = target.take_damage(damage)
        return {'damage': actual, 'critical': critical, 'target': target}

    def execute_spell(self, caster, spell, targets):
        results = []
        if not caster.use_mp(spell.get('mp_cost', 0)):
            return [{'miss': True, 'reason': 'Not enough MP'}]

        for target in targets:
            if spell['type'] == 'heal':
                heal_amount = int(caster.mag * spell['power'] * random.uniform(0.9, 1.1))
                actual = target.heal(heal_amount)
                results.append({'heal': actual, 'target': target})

            elif spell['type'] == 'revive':
                if not target.alive:
                    target.alive = True
                    target.hp = int(target.max_hp * spell['power'])
                    results.append({'revive': True, 'target': target, 'hp': target.hp})
                else:
                    results.append({'miss': True, 'target': target})

            elif spell['type'] == 'buff':
                target.defending = True  # Simplified: barrier = defending
                results.append({'buff': 'Barrier', 'target': target})

            elif spell['type'] in ('magic', 'physical'):
                stat = caster.mag if spell['type'] == 'magic' else caster.atk
                base = int(stat * spell['power'])
                variance = random.uniform(0.85, 1.15)
                damage = max(1, int(base * variance))

                # Check weakness
                element = spell.get('element', 'none')
                actual = target.take_damage(damage, element)

                weak = hasattr(target, 'weakness') and target.weakness == element
                results.append({
                    'damage': actual, 'target': target,
                    'element': element, 'weak': weak
                })

        return results

    def execute_item(self, user, item, target):
        if item['count'] <= 0:
            return {'miss': True, 'reason': 'No items left'}

        item['count'] -= 1

        if item['type'] == 'heal_hp':
            actual = target.heal(item['power'])
            return {'heal': actual, 'target': target, 'item': item['name']}

        elif item['type'] == 'heal_mp':
            target.restore_mp(item['power'])
            return {'restore_mp': item['power'], 'target': target, 'item': item['name']}

        elif item['type'] == 'revive':
            if not target.alive:
                target.alive = True
                target.hp = int(target.max_hp * item['power'])
                return {'revive': True, 'target': target, 'item': item['name']}
            return {'miss': True, 'target': target}

        return {'miss': True}

    def try_flee(self):
        if not self.can_flee:
            return False
        # 50% chance to flee, +10% per speed advantage
        avg_hero_spd = sum(m.spd for m in self.party.get_alive_members()) / max(1, len(self.party.get_alive_members()))
        avg_mon_spd = sum(m.spd for m in self.monsters if m.alive) / max(1, len([m for m in self.monsters if m.alive]))
        chance = 0.5 + (avg_hero_spd - avg_mon_spd) * 0.05
        return random.random() < max(0.2, min(0.9, chance))

    def _calculate_rewards(self):
        self.total_exp = sum(m.exp_reward for m in self.monsters)
        self.total_gold = sum(m.gold_reward for m in self.monsters)
        self.party.gold += self.total_gold

        # Distribute EXP
        alive = self.party.get_alive_members()
        if alive:
            exp_each = self.total_exp // len(alive)
            for member in alive:
                if member.gain_exp(exp_each):
                    self.leveled_up.append(member)

    def get_usable_items(self):
        return [item for item in self.party.inventory if item['count'] > 0]

    def get_alive_monsters(self):
        return [m for m in self.monsters if m.alive]
