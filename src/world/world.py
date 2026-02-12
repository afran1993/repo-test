import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


from src.i18n import t_data


class Area:
    def __init__(self, id_, data: dict, connections=None, region=None):
        # data is the original dict from JSON (may contain name/name_key/desc/desc_key)
        self.id = id_
        self.data = data
        self.connections = connections or []
        self.region = region

    def describe(self, player):
        name = t_data(self.data, 'name_key', 'name')
        desc = t_data(self.data, 'desc_key', 'desc')
        return f"{name}\n{desc}"


class Region:
    def __init__(self, id_, name, climate, areas):
        self.id = id_
        self.name = name
        self.climate = climate
        self.areas = {a['id']: Area(a['id'], a, a.get('connections', []), id_) for a in areas}


class World:
    def __init__(self, data_file=None):
        data_file = data_file or os.path.join(ROOT, 'data', 'regions.json')
        self.regions = {}
        self.load(data_file)

    def load(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for r in data.get('regions', []):
            self.regions[r['id']] = Region(r['id'], r['name'], r.get('climate','temperate'), r.get('areas', []))

    def get_area(self, region_id, area_id):
        reg = self.regions.get(region_id)
        if not reg:
            return None
        return reg.areas.get(area_id)
