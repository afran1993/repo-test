#!/usr/bin/env python3
"""Test del sistema di elementi."""

import sys
import random

# Setup seed per risultati reproducibili
random.seed(42)

from rpg import Player, load_data, get_location, fight

def test_elements():
    """Testa il sistema di elementi."""
    print("="*60)
    print("TEST SISTEMA DI ELEMENTI")
    print("="*60)
    
    # Carica i dati
    locations_data, enemies_data, items_data = load_data()
    
    # Crea un player
    player = Player("Tester")
    player.level = 3
    player.hp = player.get_total_max_hp()
    
    # Equip elemental weapons
    fire_sword = items_data.get("sword_fire", {})
    if fire_sword:
        player.equipped_weapon = fire_sword
        print(f"✓ Equipaggiato: {fire_sword.get('name', 'Fire Sword')} (elemento: {fire_sword.get('element', 'None')})\n")
    
    # Testa combattimenti in diverse location
    locations_to_test = ["fire_volcano", "water_lagoon", "earth_forest"]
    
    for loc_id in locations_to_test:
        location = get_location(loc_id, locations_data)
        if not location:
            print(f"✗ Location non trovata: {loc_id}")
            continue
        
        print(f"\n{'='*60}")
        print(f"Location: {location.name} (Elemento: {location.element})")
        print(f"Descrizione: {location.description}")
        print(f"{'='*60}")
        
        # Prova a combattere
        enemy = location.get_random_enemy(enemies_data)
        if enemy:
            print(f"Nemico: {enemy.name} (Elemento: {enemy.element})")
            print(f"Player HP: {player.hp}/{player.get_total_max_hp()}")
            print(f"Weapon Element: {player.equipped_weapon.get('element', 'None')}")
            
            # Simula 3 round di combattimento
            print("\n--- Inizio combattimento (3 round simulati) ---\n")
            for round_num in range(3):
                if not (player.is_alive() and enemy.is_alive()):
                    break
                
                print(f"Round {round_num + 1}:")
                
                # Attacco del player
                dmg = player.attack(enemy)
                weapon_element = player.equipped_weapon.get("element", "None") if player.equipped_weapon else "None"
                from rpg import get_element_modifier
                element_modifier = get_element_modifier(weapon_element, enemy.element)
                dmg = int(dmg * element_modifier)
                
                if element_modifier > 1.0:
                    print(f"  ✓ {player.name} attacca con {weapon_element} vs {enemy.element}: È super efficace!")
                elif element_modifier < 1.0:
                    print(f"  ✗ {player.name} attacca con {weapon_element} vs {enemy.element}: Non è molto efficace...")
                else:
                    print(f"  • {player.name} attacca per {dmg} danni")
                
                if not random.random() < 0.2:
                    enemy.hp -= dmg
                    print(f"    Danno inferto: {dmg} | {enemy.name} HP: {enemy.hp}/{enemy.max_hp}")
                
                if enemy.is_alive():
                    # Attacco del nemico
                    edmg = random.randint(max(1, enemy.atk - 2), enemy.atk + 2)
                    enemy_element_modifier = get_element_modifier(enemy.element, weapon_element)
                    edmg = int(edmg * enemy_element_modifier)
                    
                    if enemy_element_modifier > 1.0:
                        print(f"  ✓ {enemy.name} attacca con {enemy.element} vs {weapon_element}: È super efficace!")
                    elif enemy_element_modifier < 1.0:
                        print(f"  ✗ {enemy.name} attacca con {enemy.element} vs {weapon_element}: Non è molto efficace...")
                    else:
                        print(f"  • {enemy.name} attacca per {edmg} danni")
                    
                    if not random.random() < player.get_evasion_chance():
                        player.hp -= edmg
                        print(f"    Danno subito: {edmg} | {player.name} HP: {player.hp}/{player.get_total_max_hp()}")
                
                print()
            
            # Reset per prossimo test
            player.hp = player.get_total_max_hp()
            enemy.hp = enemy.max_hp
        else:
            print("Nessun nemico trovato in questa location")
    
    print(f"\n{'='*60}")
    print("TEST COMPLETATO!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    test_elements()
