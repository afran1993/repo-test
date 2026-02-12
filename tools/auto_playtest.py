#!/usr/bin/env python3
"""
Automated playtest script for the text RPG.
- Simula esplorazioni, dialoghi, combattimenti, loot, crafting, save/load.
- Registra errori, anomalie e produce un report JSON in `tools/playtest_report.json`.

Design:
- `AutoGameTester` organizza scenari e raccoglie log.
- Usa chiamate non-interattive alle API dell'engine e patcha `input()` quando necessario.
"""
import sys
import os
import json
import random
import traceback
from types import GeneratorType
from contextlib import contextmanager

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.engine import GameEngine
from src.skills.abilities import use_ability, CLASS_ABILITIES
from src.enemies.abilities import use_enemy_ability
from src.combat.combat import calculate_damage

REPORT_PATH = os.path.join(os.path.dirname(__file__), 'playtest_report.json')


@contextmanager
def mock_input(responses):
    """Context manager that replaces builtins.input with a generator of responses."""
    import builtins
    if isinstance(responses, GeneratorType) or isinstance(responses, list):
        gen = (r for r in responses)
    else:
        # single value
        gen = (r for r in [responses])
    old = builtins.input

    def _inp(prompt=''):
        try:
            return next(gen)
        except StopIteration:
            # default to empty input
            return ''

    builtins.input = _inp
    try:
        yield
    finally:
        builtins.input = old


class AutoGameTester:
    def __init__(self, seed=42, max_turns=100):
        random.seed(seed)
        self.engine = GameEngine()
        self.logs = []
        self.errors = []
        self.warnings = []
        self.max_turns = max_turns
        self._prepare()

    def _log(self, level, msg):
        self.logs.append({'level': level, 'msg': msg})

    def _prepare(self):
        try:
            # pick a random archetype if available
            arch_keys = list(self.engine.archetypes.keys())
            if not arch_keys:
                arch = 'warrior'
            else:
                arch = random.choice(arch_keys)
            self.engine.create_player('AutoTester', arch)
            self.engine.instantiate_npcs()
            # set a starting location
            self.engine.player_location = ('hearthvale', 'town_square')
            self._log('info', f'Created player AutoTester as {arch}')
        except Exception as e:
            self._record_error('prepare', e)

    def _record_error(self, phase, exc):
        tb = traceback.format_exc()
        self.errors.append({'phase': phase, 'error': str(exc), 'trace': tb})
        self._log('error', f'[{phase}] {exc}')

    def explore_world(self, steps=10):
        try:
            regions = list(self.engine.world.regions.keys())
            for i in range(steps):
                # choose region and area randomly
                region = random.choice(regions)
                areas = list(self.engine.world.regions[region].areas.keys())
                area = random.choice(areas)
                self.engine.player_location = (region, area)
                desc = self.engine.describe_location()
                self._log('info', f'Explore to {region}/{area}')
                # sometimes tick world
                if random.random() < 0.3:
                    self.engine.tick_world(time_of_day=random.randint(0,3))
        except Exception as e:
            self._record_error('explore_world', e)

    def interact_with_npcs(self, attempts=5):
        try:
            # try talking in the current location and nearby
            for _ in range(attempts):
                region, area = self.engine.player_location
                # find NPCs present according to engine._handle_talk lookup
                npcs_here = [n for n in self.engine.npcs.get('npcs', []) if n.get('location') == {'region': region, 'area': area}]
                if not npcs_here:
                    # move to first NPC location if any
                    all_npcs = self.engine.npcs.get('npcs', [])
                    if not all_npcs:
                        return
                    target_n = random.choice(all_npcs)
                    loc = target_n.get('location', {})
                    self.engine.player_location = (loc.get('region'), loc.get('area'))
                    self._log('info', f'Moved to NPC location {self.engine.player_location}')
                    npcs_here = [target_n]

                npc = random.choice(npcs_here)
                # run dialogue; engine._handle_talk builds a small dialog and calls run_dialogue which reads input
                # prepare responses: pick first choice then end
                responses = ['1', '2']
                with mock_input(responses):
                    try:
                        self.engine._handle_talk(npc.get('id'))
                        self._log('info', f'Talked to {npc.get("id")}')
                    except Exception as e:
                        self._record_error('interact_with_npcs', e)
        except Exception as e:
            self._record_error('interact_with_npcs', e)

    def simulate_combat(self, fights=6):
        try:
            for i in range(fights):
                # spawn random enemy in region
                region = random.choice(list(self.engine.world.regions.keys()))
                enemy = self.engine.spawn_enemy(region=region)
                if not enemy:
                    self._log('warn', 'No enemy spawned')
                    continue
                self._log('info', f'Start combat vs {enemy.name}')
                # simple combat loop with caps
                turns = 0
                while self.engine.player.is_alive() and enemy.is_alive() and turns < self.max_turns:
                    # player action: try ability if any
                    arch = self.engine.player.archetype
                    abilities = CLASS_ABILITIES.get(arch, [])
                    acted = False
                    if abilities and random.random() < 0.7:
                        abil = random.choice(abilities)
                        try:
                            res = use_ability(abil, self.engine.player, enemy)
                            self._log('info', f'Player used {abil} -> {res}')
                            acted = True
                        except Exception as e:
                            self._record_error('simulate_combat_use_ability', e)
                    if not acted:
                        # basic attack
                        dmg = calculate_damage(self.engine.player, enemy)
                        enemy.hp -= dmg
                        self._log('info', f'Player attack deals {dmg}')

                    # check enemy death
                    if not enemy.is_alive():
                        self._log('info', f'Enemy {enemy.name} defeated')
                        break

                    # enemy acts
                    try:
                        # use_enemy_ability may return spawn instructions
                        from src.enemies.ai import choose_enemy_action
                        action = choose_enemy_action(enemy, self.engine.player, engine=self.engine)
                        if action.get('type') == 'ability' and enemy.abilities:
                            res = use_enemy_ability(action.get('ability'), enemy, self.engine.player, engine=self.engine)
                            self._log('info', f'Enemy used ability -> {res}')
                        else:
                            dmg = calculate_damage(enemy, self.engine.player)
                            self.engine.player.hp -= dmg
                            self._log('info', f'Enemy attack deals {dmg}')
                    except Exception as e:
                        self._record_error('simulate_combat_enemy_act', e)

                    # tick statuses
                    try:
                        p_applied = self.engine.player.tick_statuses()
                        e_applied = enemy.tick_statuses()
                        if p_applied:
                            self._log('info', f'Player statuses applied {p_applied}')
                        if e_applied:
                            self._log('info', f'Enemy statuses applied {e_applied}')
                    except Exception as e:
                        self._record_error('simulate_combat_tick', e)

                    turns += 1

                if turns >= self.max_turns:
                    self.warnings.append({'type': 'turn_limit', 'enemy': enemy.name})
                # on death, roll drops
                if not enemy.is_alive():
                    try:
                        drops = enemy.roll_drops()
                        # give to player
                        self.engine.player.gold = getattr(self.engine.player, 'gold', 0) + drops.get('gold', 0)
                        for it in drops.get('items', []):
                            self.engine.player.inventory.append({'id': it, 'display': it})
                        self._log('info', f'Drops: {drops}')
                        # check items reference validity
                        items_data = [it.get('id') for it in self.engine.items]
                        for iid in drops.get('items', []):
                            if iid not in items_data:
                                self.warnings.append({'type': 'missing_item_def', 'item': iid})
                    except Exception as e:
                        self._record_error('simulate_combat_drops', e)

                # heal player a bit between fights
                self.engine.player.hp = min(self.engine.player.max_hp, self.engine.player.hp + 10)
        except Exception as e:
            self._record_error('simulate_combat', e)

    def simulate_crafting(self):
        try:
            # Very small mock crafting: if player has a stone_fragment and bone_fragment, craft a 'makeshift_knife'
            inv_ids = [it.get('id') for it in self.engine.player.inventory]
            if 'stone_fragment' in inv_ids and 'bone_fragment' in inv_ids:
                # remove materials
                removed = 0
                new_inv = []
                for it in self.engine.player.inventory:
                    if it.get('id') in ('stone_fragment','bone_fragment') and removed < 2:
                        removed += 1
                        continue
                    new_inv.append(it)
                self.engine.player.inventory = new_inv
                crafted = {'id': 'makeshift_knife', 'display': 'Makeshift Knife', 'stats': {'atk': 2}}
                self.engine.player.inventory.append(crafted)
                self._log('info', f'Crafted {crafted["id"]}')
            else:
                self._log('info', 'No materials for crafting')
        except Exception as e:
            self._record_error('simulate_crafting', e)

    def test_dialogue_branching(self):
        try:
            # Build a branching dialogue and walk multiple paths via mock input
            from src.dialogue.dialogue import DialogueNode, run_dialogue
            node_map = {
                'start': DialogueNode('start', 'You meet a stranger.', [('Greet','greet'),('Threaten','threat')]),
                'greet': DialogueNode('greet','They smile.', [('Ask Quest','quest'),('Bye','end')]),
                'threat': DialogueNode('threat','They recoil.', [('Attack','attack'),('Back','start')]),
                'quest': DialogueNode('quest','They ask you to fetch a gem.', [('Accept','accept'),('Decline','decline')]),
                'accept': DialogueNode('accept','You accept the quest.', []),
                'decline': DialogueNode('decline','You decline.', []),
                'attack': DialogueNode('attack','Combat!', []) ,
                'end': DialogueNode('end','Farewell.', [])
            }
            # First path: greet -> ask quest -> accept
            with mock_input(['1','1','1']):
                run_dialogue(node_map,'start')
            # Second path: threaten -> back -> greet -> bye
            with mock_input(['2','2','1','2']):
                run_dialogue(node_map,'start')
            self._log('info', 'Dialogue branching tested')
        except Exception as e:
            self._record_error('test_dialogue_branching', e)

    def test_save_load(self):
        try:
            path = os.path.join(os.path.dirname(__file__), 'tmp_save.json')
            # ensure some inventory
            self.engine.player.inventory.append({'id':'test_token','display':'Token'})
            self.engine.save(path)
            # mutate
            self.engine.player.inventory = []
            self.engine.load(path)
            # verify token present
            inv_ids = [it.get('id') for it in self.engine.player.inventory]
            if 'test_token' not in inv_ids:
                self.warnings.append({'type':'save_load_mismatch','msg':'test_token missing after load'})
            else:
                self._log('info','Save/load OK')
        except Exception as e:
            self._record_error('test_save_load', e)

    def run_all(self):
        try:
            self.explore_world(steps=8)
            self.interact_with_npcs(attempts=6)
            self.simulate_combat(fights=8)
            self.simulate_crafting()
            self.test_dialogue_branching()
            self.test_save_load()
        except Exception as e:
            self._record_error('run_all', e)
        finally:
            self._finalize()

    def _finalize(self):
        report = {
            'logs': self.logs,
            'errors': self.errors,
            'warnings': self.warnings,
            'player': {
                'name': getattr(self.engine.player,'name',None),
                'hp': getattr(self.engine.player,'hp',None),
                'level': getattr(self.engine.player,'level',None),
                'gold': getattr(self.engine.player,'gold',None),
                'inventory': [it.get('id') for it in self.engine.player.inventory]
            }
        }
        try:
            with open(REPORT_PATH, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print('Playtest report written to', REPORT_PATH)
        except Exception as e:
            print('Failed writing report:', e)


if __name__ == '__main__':
    t = AutoGameTester()
    t.run_all()
