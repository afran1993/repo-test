#!/usr/bin/env python3
"""Extract translatable strings from data/ into locales/en-missing.json.

This scans common data files and writes keys for any fields that are raw text
(`display`, `name`, `desc`, `title`, `description`, `stages`) that don't have
corresponding `_key` fields.
"""
import json
import os
from glob import glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(ROOT, 'data')
OUT = os.path.join(ROOT, 'locales', 'en-missing.json')


def add(mapping, key, text):
    if not text:
        return
    if key in mapping and mapping[key] != text:
        # avoid overwriting different text
        return
    mapping[key] = text


def scan_items(mapping):
    path = os.path.join(DATA_DIR, 'items.json')
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        items = json.load(f)
    for it in items:
        iid = it.get('id')
        if not iid:
            continue
        if not it.get('name_key') and it.get('display'):
            add(mapping, f"item.{iid}.name", it.get('display'))
        if not it.get('desc_key') and it.get('desc'):
            add(mapping, f"item.{iid}.desc", it.get('desc'))


def scan_archetypes(mapping):
    path = os.path.join(DATA_DIR, 'archetypes.json')
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for k,v in data.items():
        if not v.get('key') and v.get('display'):
            add(mapping, f"class.{k}.name", v.get('display'))


def scan_regions(mapping):
    path = os.path.join(DATA_DIR, 'regions.json')
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for r in data.get('regions', []):
        rid = r.get('id')
        if r.get('name') and not r.get('name_key'):
            add(mapping, f"region.{rid}.name", r.get('name'))
        for a in r.get('areas', []):
            aid = a.get('id')
            if a.get('name') and not a.get('name_key'):
                add(mapping, f"region.{rid}.area.{aid}.name", a.get('name'))
            if a.get('desc') and not a.get('desc_key'):
                add(mapping, f"region.{rid}.area.{aid}.desc", a.get('desc'))


def scan_npcs(mapping):
    path = os.path.join(DATA_DIR, 'npcs.json')
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for n in data.get('npcs', []):
        nid = n.get('id')
        if n.get('name') and not n.get('name_key'):
            add(mapping, f"npc.{nid}.name", n.get('name'))


def scan_quests(mapping):
    path = os.path.join(DATA_DIR, 'quests.json')
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for q in data.get('quests', []):
        qid = q.get('id')
        if q.get('title') and not q.get('title_key'):
            add(mapping, f"quest.{qid}.title", q.get('title'))
        if q.get('description') and not q.get('description_key'):
            add(mapping, f"quest.{qid}.description", q.get('description'))
        for i, s in enumerate(q.get('stages', []), 1):
            if s:
                add(mapping, f"quest.{qid}.stage.{i}", s)


def main():
    mapping = {}
    scan_items(mapping)
    scan_archetypes(mapping)
    scan_regions(mapping)
    scan_npcs(mapping)
    scan_quests(mapping)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print('Wrote', OUT, 'with', len(mapping), 'entries')


if __name__ == '__main__':
    main()
