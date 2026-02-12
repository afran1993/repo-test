import os
import sys
import json

# Ensure repo root is on sys.path so we can import package modules
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.world.world import World
from src.characters.character import PlayerCharacter, NPC
from src.items.item import Item
from src.combat.combat import turn_based_fight
from src.dialogue.dialogue import run_dialogue
from src.quests.quest import Quest
from src.commands import parse_command, normalize_target


class GameEngine:
    def __init__(self):
        self.world = World()
        self.items = self._load_json(os.path.join(REPO_ROOT, 'data', 'items.json'))
        self.archetypes = self._load_json(os.path.join(REPO_ROOT, 'data', 'archetypes.json'))
        self.npcs = self._load_json(os.path.join(REPO_ROOT, 'data', 'npcs.json'))
        self.quests = self._load_json(os.path.join(REPO_ROOT, 'data', 'quests.json'))
        self.player = None

    def _load_json(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def create_player(self, name, archetype_key):
        base = self.archetypes.get(archetype_key, {}).get('base_stats', {})
        # map base stats to RPG stats (str,dex,int,cha,end)
        stats = {
            'str': base.get('atk', 5),
            'dex': 5,
            'int': 5,
            'cha': 5,
            'end': base.get('def', 5)
        }
        pc = PlayerCharacter('player', name, archetype_key, stats=stats)
        # starter items
        pc.inventory.append({'id':'potion_small','display':'Small Potion'})
        self.player = pc
        print(f"Created player {pc.name} as {archetype_key}.")

    def save(self, path='savegame.json'):
        data = {'player': self._serialize_player()}
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print('Game saved.')

    def _serialize_player(self):
        p = self.player
        return {'id': p.id, 'name': p.name, 'archetype': p.archetype, 'level': p.level, 'hp': p.hp, 'inventory': p.inventory}

    def load(self, path='savegame.json'):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            pd = data.get('player', {})
            self.create_player(pd.get('name','Hero'), pd.get('archetype','warrior'))
            self.player.level = pd.get('level',1)
            self.player.hp = pd.get('hp', self.player.max_hp)
            self.player.inventory = pd.get('inventory', [])
            print('Game loaded.')
        except Exception:
            print('No save found.')

    def start(self):
        print('Welcome to the Open-World Text RPG (prototype).')
        # simple setup
        name = input('Name: ').strip() or 'Hero'
        print('Choose class:')
        keys = list(self.archetypes.keys())
        for i,k in enumerate(keys,1):
            print(f"{i}) {self.archetypes[k]['display']} ({k})")
        idx = int(input('-> ').strip() or '1') - 1
        arche = keys[max(0,min(idx,len(keys)-1))]
        self.create_player(name, arche)
        # starting area
        self.player_location = ('hearthvale','town_square')
        self.loop()

    def describe_location(self):
        region, area = self.player_location
        a = self.world.get_area(region, area)
        if a:
            print('\n' + a.describe(self.player))

    def loop(self):
        while True:
            self.describe_location()
            line = input('\n> ').strip()
            verb, args = parse_command(line)
            if not verb:
                continue
            if verb in ('quit','exit'):
                print('Goodbye.')
                break
            if verb in ('look','l'):
                self.describe_location()
            elif verb == 'talk':
                target = normalize_target(args)
                self._handle_talk(target)
            elif verb in ('move','go'):
                target = normalize_target(args)
                self._handle_move(target)
            elif verb in ('attack','fight'):
                target = normalize_target(args)
                self._handle_attack(target)
            elif verb == 'inventory':
                print('Inventory:')
                for it in self.player.inventory:
                    print('-', it.get('display', it.get('id')))
            elif verb == 'save':
                self.save()
            elif verb == 'load':
                self.load()
            else:
                print('Unknown command.')

    def _handle_talk(self, target):
        # find NPC in current area
        region, area = self.player_location
        npcs = [n for n in self.npcs.get('npcs', []) if n.get('location') == {'region':region,'area':area}]
        if not target:
            if npcs:
                target = npcs[0]['id']
        if not target:
            print('No one to talk to here.')
            return
        npc_data = next((n for n in npcs if n['id']==target or n['name'].lower()==target.lower()), None)
        if not npc_data:
            print('No such person here.')
            return
        # basic dialogue
        dialog = { 'start': ('Hello traveler. What do you want?', [('Ask about town','ask_town'),('Goodbye','end')]),
                   'ask_town': ('Hearthvale is peaceful...', [('Back','start'), ('Goodbye','end')]) }
        node_map = {
            'start': type('N',(),{'text':dialog['start'][0],'choices':dialog['start'][1]}),
            'ask_town': type('N',(),{'text':dialog['ask_town'][0],'choices':dialog['ask_town'][1]}),
            'end': type('N',(),{'text':'Farewell.','choices':[]})
        }
        run_dialogue(node_map,'start')

    def _handle_move(self, target):
        if not target:
            print('Where to?')
            return
        # naive: allow 'to <area>' or area id
        region, area = self.player_location
        reg = self.world.regions.get(region)
        if not reg:
            print('You are lost.')
            return
        # find area by name or id
        dest = None
        for a in reg.areas.values():
            if a.id == target or a.name.lower()==target.lower():
                dest = a
        if dest:
            self.player_location = (region, dest.id)
            print(f'You move to {dest.name}.')
        else:
            print('Cannot go there.')

    def _handle_attack(self, target):
        # spawn a dummy enemy for demo
        enemy = NPC('gob1','Goblin', level=1, stats={'str':6,'end':3})
        from src.combat.combat import turn_based_fight
        turn_based_fight(self.player, enemy, self)


if __name__ == '__main__':
    g = GameEngine()
    g.start()
