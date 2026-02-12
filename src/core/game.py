#!/usr/bin/env python3
import json
import os
import textwrap


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


ARCHETYPES = load_json(os.path.join(ROOT, 'data', 'archetypes.json'))
ITEMS = load_json(os.path.join(ROOT, 'data', 'items.json'))
LOCALE = load_json(os.path.join(ROOT, 'locales', 'en.json'))


def t(key):
    return LOCALE.get(key, key)


def list_classes():
    for i, k in enumerate(ARCHETYPES.keys(), 1):
        print(f"{i}) {ARCHETYPES[k]['display']} ({k})")


def list_items():
    for i, it in enumerate(ITEMS, 1):
        print(f"{i}) {it['display']} - {it['weapon_type']}")


def can_equip(archetype_key, item):
    # Check explicit allowed_classes first
    if 'allowed_classes' in item and item['allowed_classes']:
        if archetype_key in item['allowed_classes']:
            return True
    # Check archetype allowed weapons
    allowed = ARCHETYPES[archetype_key]['allowed_weapons']
    return item.get('weapon_type') in allowed


def demo_cli():
    print(textwrap.dedent('''
    Prototype: Class & Equipment rules demo
    - The game is data-driven: archetypes and items are in JSON
    - This demo shows equip validation and basic element/item metadata
    '''))

    print(t('msg.choose_class'))
    keys = list(ARCHETYPES.keys())
    list_classes()
    idx = int(input('-> ').strip() or '1') - 1
    archetype = keys[max(0, min(idx, len(keys)-1))]
    print(f"Selected: {ARCHETYPES[archetype]['display']} ({archetype})")

    print('\n' + t('msg.choose_item'))
    list_items()
    idx = int(input('-> ').strip() or '1') - 1
    item = ITEMS[max(0, min(idx, len(ITEMS)-1))]

    ok = can_equip(archetype, item)
    if ok:
        print(t('msg.can_equip'))
        print('Item details:', item)
    else:
        print(t('msg.cannot_equip'))


if __name__ == '__main__':
    demo_cli()
