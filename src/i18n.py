import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class I18n:
    def __init__(self, default='en'):
        self.locale = default
        self.locales = {}
        self.load_locales()

    def load_locales(self):
        for name in ('en','it'):
            path = os.path.join(ROOT, 'locales', f'{name}.json')
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.locales[name] = json.load(f)
            except Exception:
                self.locales[name] = {}

    def set_locale(self, name):
        if name in self.locales:
            self.locale = name

    def t(self, key, **kwargs):
        txt = self.locales.get(self.locale, {}).get(key) or self.locales.get('en', {}).get(key) or key
        try:
            return txt.format(**kwargs)
        except Exception:
            return txt


i18n = I18n()

def t(key, **kwargs):
    return i18n.t(key, **kwargs)


def t_data(entry: dict, key_name: str, fallback_field: str):
    """Return localized text for a data entry.

    - entry: the dict from data files
    - key_name: the localization key field name, e.g. 'name_key' or 'desc_key'
    - fallback_field: the field with raw text, e.g. 'display' or 'desc'
    """
    if not entry:
        return ''
    key = entry.get(key_name)
    if key:
        return i18n.t(key)
    return entry.get(fallback_field, '')
