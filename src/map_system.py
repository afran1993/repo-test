"""
Map system - visualizza la posizione del giocatore e permette navigazione tra locazioni
Ispirato da Arcania Gothic: mostra mappa, connessioni, e permette di muoversi
"""

import json
from src.i18n import i18n

def print_map(current_location_id, locations_data):
    """
    Visualizza una mappa ASCII mostrando:
    - Posizione attuale (evidenziata)
    - Locazioni collegate
    - Distanza/difficoltà
    """
    current = locations_data.get(current_location_id, {})
    current_name = current.get('name', 'Unknown')
    connections = current.get('connections', {})
    
    print("\n" + "="*70)
    print(i18n.t('map.title', 'MAPPA DEL MONDO'))
    print("="*70)
    print(f"\n📍 {i18n.t('map.current_location', 'Posizione attuale')}: \033[96m{current_name}\033[0m")
    print(f"   {i18n.t('map.difficulty', 'Difficoltà')}: {_get_difficulty_str(current.get('difficulty', 0))}")
    print(f"   {i18n.t('map.terrain', 'Terreno')}: {current.get('terrain', 'unknown')}")
    print(f"   {current.get('description', '')}\n")
    
    if connections:
        print(f"🚩 {i18n.t('map.connections', 'Connessioni disponibili')}:\n")
        for idx, (direction, location_id) in enumerate(connections.items(), 1):
            location = locations_data.get(location_id, {})
            difficulty = location.get('difficulty', 0)
            name = location.get('name', 'Unknown')
            
            # Calcola emoji difficoltà
            if difficulty == 0:
                diff_emoji = "✅"
            elif difficulty <= 1.5:
                diff_emoji = "⚠️"
            elif difficulty <= 2.5:
                diff_emoji = "⚡"
            else:
                diff_emoji = "💀"
            
            print(f"  {idx}. [{direction.upper()}] {name}")
            print(f"     Difficoltà: {diff_emoji} ({difficulty})")
            print()
    else:
        print(f"❌ {i18n.t('map.no_connections', 'Nessuna connessione disponibile')}\n")
    
    print("="*70 + "\n")


def show_world_map():
    """
    Visualizza una mappa del mondo complessiva con tutte le locazioni
    che il giocatore ha scoperto
    """
    with open('data/locations.json') as f:
        locations_data = json.load(f)['locations']
    
    locations = {loc['id']: loc for loc in locations_data}
    
    print("\n" + "="*70)
    print(i18n.t('map.world_map', 'MAPPA DEL MONDO COMPLETA'))
    print("="*70)
    
    # Raggruppa per difficoltà
    by_difficulty = {}
    for loc in locations_data:
        diff = loc.get('difficulty', 0)
        if diff not in by_difficulty:
            by_difficulty[diff] = []
        by_difficulty[diff].append(loc)
    
    for diff in sorted(by_difficulty.keys()):
        locations_at_diff = by_difficulty[diff]
        diff_level = _get_difficulty_str(diff)
        print(f"\n📍 {diff_level} ({diff})")
        print("-" * 70)
        
        for loc in locations_at_diff:
            element = loc.get('element', 'None')
            emoji = _get_element_emoji(element)
            connections_count = len(loc.get('connections', {}))
            
            print(f"  • {loc['name']:<35} {emoji:>3}  |  {connections_count} connessioni")
    
    print("\n" + "="*70 + "\n")


def _get_difficulty_str(difficulty):
    """Ritorna stringa di difficoltà formattata"""
    if difficulty == 0:
        return "🟢 FACILE"
    elif difficulty <= 1.5:
        return "🟡 MEDIO"
    elif difficulty <= 2.5:
        return "🔴 DIFFICILE"
    else:
        return "⚫ MOLTO DIFFICILE"


def _get_element_emoji(element):
    """Ritorna emoji per elemento"""
    emojis = {
        'Fire': '🔥',
        'Ice': '❄️',
        'Water': '💧',
        'Earth': '🌿',
        'Air': '💨',
        'Lightning': '⚡',
        'Arcane': '🌀',
        'None': '⚪'
    }
    return emojis.get(element, '?')


def list_locations(locations_data):
    """Mostra elenco di tutte le locazioni disponibili"""
    locations = sorted(
        locations_data.values(),
        key=lambda x: x.get('difficulty', 0)
    )
    
    print("\n" + "="*70)
    print(i18n.t('map.all_locations', 'TUTTE LE LOCAZIONI'))
    print("="*70 + "\n")
    
    for idx, loc in enumerate(locations, 1):
        difficulty = loc.get('difficulty', 0)
        element = loc.get('element', 'None')
        enemy_count = len(loc.get('enemies', []))
        
        print(f"{idx:2}. {loc['name']:<30} | Diff: {difficulty:>3} | Nemici: {enemy_count:>2}")
    
    print("\n" + "="*70 + "\n")


def navigate_location(player, current_location_id, direction, locations_data):
    """
    Permette al giocatore di navigare verso una locazione connessa
    
    Returns:
        (success: bool, new_location_id: str or None, message: str)
    """
    current = locations_data.get(current_location_id, {})
    connections = current.get('connections', {})
    
    # Normalizza direzione input
    direction = direction.lower().strip()
    
    # Cerca la connessione
    target_location_id = None
    for conn_dir, loc_id in connections.items():
        if conn_dir.lower() == direction:
            target_location_id = loc_id
            break
    
    if not target_location_id:
        available = ", ".join(connections.keys())
        msg = i18n.t('map.invalid_direction', f'Direzione non valida. Disponibili: {available}')
        return (False, None, msg)
    
    target = locations_data.get(target_location_id, {})
    target_name = target.get('name', 'Unknown')
    difficulty = target.get('difficulty', 0)
    
    # Messaggio di movimento
    msg = i18n.t('map.moving_to', f'Ti muovi verso: {target_name}...')
    
    return (True, target_location_id, msg)
