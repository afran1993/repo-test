#!/usr/bin/env python3
"""
Analisi e integrazione nemici mancanti
Legge enemies.json e locations.json per trovare nemici non utilizzati
e suggerire dove integrarli.
"""

import json

# Carica i file
with open('data/enemies.json', 'r') as f:
    enemies_data = json.load(f)

with open('data/locations.json', 'r') as f:
    locations_data = json.load(f)

# Estrai tutti gli ID nemici definiti
all_enemy_ids = {enemy['id'] for enemy in enemies_data['enemies']}

# Estrai tutti i nemici usati nelle locazioni
used_enemy_ids = set()
for location in locations_data['locations']:
    for enemy in location.get('enemies', []):
        used_enemy_ids.add(enemy['id'])

# Nemici non usati
unused = sorted(all_enemy_ids - used_enemy_ids)

print(f"Total enemies defined: {len(all_enemy_ids)}")
print(f"Enemies used in locations: {len(used_enemy_ids)}")
print(f"Unused enemies: {len(unused)}\n")

# Filtra solo gli "natural" nemici rilevanti (non i FF/DQ/LoZ che sono reference)
natural_enemies = []
for enemy_id in unused:
    enemy = next((e for e in enemies_data['enemies'] if e['id'] == enemy_id), None)
    if enemy and not any(p in enemy_id for p in ['ff_', 'dq_', 'loz_', 'lod_', 'ds_', 'mh_', 'risen_', 'tw_', 'sky_']):
        natural_enemies.append((enemy_id, enemy))

print(f"Natural enemies (excluding game references): {len(natural_enemies)}\n")

# Raggruppa per elemento
by_element = {}
for enemy_id, enemy in natural_enemies:
    element = enemy.get('element', 'None')
    if element not in by_element:
        by_element[element] = []
    by_element[element].append((enemy_id, enemy))

print("Natural enemies by element:")
for element, enemies in sorted(by_element.items()):
    print(f"\n{element}:")
    for eid, e in sorted(enemies, key=lambda x: x[1].get('tier', 0)):
        tags = ', '.join(e.get('tags', []))
        print(f"  - {eid}: {e['display']} (T{e.get('tier')}) [{tags}]")

# Suggerimenti di integrazione
print("\n" + "="*80)
print("SUGGERIMENTI DI INTEGRAZIONE")
print("="*80)

locations_by_id = {loc['id']: loc for loc in locations_data['locations']}

# Mapping element -> locations
element_to_locations = {
    'Fire': ['volcano_entrance', 'volcano_core'],
    'Water': ['lagoon', 'underwater_cave'],
    'Ice': ['underwater_cave', 'lagoon'],
    'Earth': ['forest_entrance', 'deep_forest', 'cave_entrance', 'cave_deep', 'mountain_path'],
    'Air': ['summit', 'sky_temple'],
    'Lightning': ['sky_temple'],
    'Arcane': ['shadow_temple', 'cave_deep']
}

for element, locations in element_to_locations.items():
    if element in by_element:
        enemies_for_element = by_element[element]
        print(f"\nLocazioni {element}:")
        for loc_id in locations:
            if loc_id in locations_by_id:
                loc = locations_by_id[loc_id]
                existing_enemies = [e['id'] for e in loc.get('enemies', [])]
                print(f"  {loc_id}: {', '.join(existing_enemies) if existing_enemies else '[nessuno ancora]'}")
        
        print(f"  → Suggested enemies for {element}:")
        for eid, e in enemies_for_element[:3]:
            print(f"    • {eid} (T{e.get('tier')})")

print("\n" + "="*80)
