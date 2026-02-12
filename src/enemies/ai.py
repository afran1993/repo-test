import random


def choose_enemy_action(enemy, target, engine=None):
    """
    Semplice selettore delle azioni nemiche basato su euristiche.
    Restituisce un dict con:
      {'type': 'ability', 'ability': 'name'} oppure {'type': 'attack'}
    """
    ability_list = getattr(enemy, 'abilities', []) or []

    # se ha abilità preferiamo valutarle con un semplice scoring
    if ability_list:
        scores = {}
        for a in ability_list:
            score = 1.0
            name = a.lower()

            # Preferenze basiche per certe abilità note
            if name in ('breath_fire', 'flame_breath') and getattr(enemy, 'element', None) == 'Fire':
                res = getattr(target, 'resistances', {}).get('Fire', 1.0)
                if res < 1.0:
                    score += 2.0

            if name == 'poison_bite':
                if 'Poison' not in getattr(target, 'immunities', []):
                    score += 1.5

            if name == 'raise_skeleton':
                # preferisce evocare se pochi alleati sono presenti
                allies = getattr(engine, 'current_enemies', []) if engine else []
                if len(allies) < 2:
                    score += 2.0

            if 'multi' in name:
                score += 0.5

            scores[a] = score

        total = sum(scores.values())
        if total > 0:
            pick = random.random() * total
            cum = 0.0
            for a, s in scores.items():
                cum += s
                if pick <= cum:
                    return {'type': 'ability', 'ability': a}

    # fallback: attacco base
    return {'type': 'attack'}
