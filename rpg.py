#!/usr/bin/env python3
import random
import json
import os
import argparse
import time


class Player:
    def __init__(self, name="Eroe"):
        self.name = name
        self.level = 1
        self.xp = 0
        self.max_hp = 30
        self.hp = self.max_hp
        self.atk = 6
        self.gold = 10
        self.potions = 2

    def is_alive(self):
        return self.hp > 0

    def attack(self, target):
        dmg = random.randint(max(1, self.atk - 2), self.atk + 2)
        target.hp -= dmg
        return dmg

    def use_potion(self):
        if self.potions <= 0:
            return 0
        heal = random.randint(8, 14)
        self.hp = min(self.max_hp, self.hp + heal)
        self.potions -= 1
        return heal

    def gain_xp(self, amount):
        self.xp += amount
        lvl_up = False
        while self.xp >= self.level * 12:
            self.xp -= self.level * 12
            self.level += 1
            self.max_hp += 6
            self.atk += 2
            self.hp = self.max_hp
            lvl_up = True
        return lvl_up

    def status(self):
        return f"{self.name} - LV {self.level}  HP {self.hp}/{self.max_hp}  ATK {self.atk}  XP {self.xp}/{self.level*12}  Gold {self.gold}  Potions {self.potions}"


class Enemy:
    def __init__(self, name, hp, atk, xp_reward, gold_reward):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward

    def is_alive(self):
        return self.hp > 0


def random_enemy(player_level):
    roll = random.random()
    if roll < 0.5:
        base = max(1, player_level)
        return Enemy("Goblin", 10 + base * 2, 3 + base, 6 + base, 4 + base)
    if roll < 0.8:
        base = max(1, player_level)
        return Enemy("Lupo", 14 + base * 3, 4 + base, 9 + base, 6 + base)
    return Enemy("Orco", 20 + player_level * 4, 6 + player_level * 2, 15 + player_level, 12 + player_level)


def fight(player, enemy):
    print(f"Incontro! {enemy.name} appare (HP {enemy.hp})")
    time.sleep(0.4)
    while player.is_alive() and enemy.is_alive():
        print()
        print(player.status())
        print(f"Nemico: {enemy.name} - HP {enemy.hp}")
        print("Scegli: (1)Attacca  (2)Pozione  (3)Fuggi")
        choice = input("-> ").strip()
        if choice == "1":
            dmg = player.attack(enemy)
            print(f"Colpisci il {enemy.name} per {dmg} danni.")
        elif choice == "2":
            healed = player.use_potion()
            if healed:
                print(f"Bevi una pozione e recuperi {healed} HP.")
            else:
                print("Non hai pozioni!")
                continue
        elif choice == "3":
            if random.random() < 0.5:
                print("Fuggi riuscita!")
                return False
            else:
                print("Non riesci a fuggire!")
        else:
            print("Scelta non valida.")
            continue

        if enemy.is_alive():
            edmg = random.randint(max(1, enemy.atk - 2), enemy.atk + 2)
            player.hp -= edmg
            print(f"{enemy.name} ti colpisce per {edmg} danni.")

    if player.is_alive():
        print(f"Hai sconfitto il {enemy.name}!")
        player.gold += enemy.gold_reward
        leveled = player.gain_xp(enemy.xp_reward)
        print(f"Ottieni {enemy.xp_reward} XP e {enemy.gold_reward} gold.")
        if leveled:
            print(f"Sei salito al livello {player.level}! HP ripristinati.")
        return True
    else:
        print("Sei stato sconfitto...")
        return False


def save_game(player, path="save.json"):
    data = {
        "name": player.name,
        "level": player.level,
        "xp": player.xp,
        "max_hp": player.max_hp,
        "hp": player.hp,
        "atk": player.atk,
        "gold": player.gold,
        "potions": player.potions,
    }
    with open(path, "w") as f:
        json.dump(data, f)
    print("Partita salvata.")


def load_game(path="save.json"):
    if not os.path.exists(path):
        print("Nessun salvataggio trovato.")
        return None
    with open(path, "r") as f:
        data = json.load(f)
    p = Player(data.get("name", "Eroe"))
    p.level = data.get("level", 1)
    p.xp = data.get("xp", 0)
    p.max_hp = data.get("max_hp", 30)
    p.hp = data.get("hp", p.max_hp)
    p.atk = data.get("atk", 6)
    p.gold = data.get("gold", 0)
    p.potions = data.get("potions", 0)
    print("Partita caricata.")
    return p


def shop(player):
    print("Bottega: (1)Pozione (5 gold)  (2)Niente")
    choice = input("-> ").strip()
    if choice == "1":
        if player.gold >= 5:
            player.gold -= 5
            player.potions += 1
            print("Acquistata pozione.")
        else:
            print("Non hai abbastanza gold.")
    else:
        print("Esci dalla bottega.")


def main_loop(player):
    print("Benvenuto nell'avventura!")
    while True:
        print()
        print(player.status())
        print("Cosa vuoi fare?")
        print("1) Esplora   2) Bottega   3) Riposa   4) Salva   5) Carica   6) Esci")
        cmd = input("-> ").strip()
        if cmd == "1":
            if random.random() < 0.75:
                enemy = random_enemy(player.level)
                result = fight(player, enemy)
                if not player.is_alive():
                    print("FINE. Vuoi ricominciare? (s/n)")
                    if input("-> ").strip().lower().startswith("s"):
                        return False
                    return True
            else:
                found = random.choice(["gold", "potion", "nothing"])
                if found == "gold":
                    g = random.randint(3, 12)
                    player.gold += g
                    print(f"Trovi {g} gold!")
                elif found == "potion":
                    player.potions += 1
                    print("Trovi una pozione!")
                else:
                    print("Niente di interessante qui.")
        elif cmd == "2":
            shop(player)
        elif cmd == "3":
            heal = min(player.max_hp - player.hp, random.randint(6, 14))
            player.hp += heal
            print(f"Riposi e recuperi {heal} HP.")
        elif cmd == "4":
            save_game(player)
        elif cmd == "5":
            loaded = load_game()
            if loaded:
                player = loaded
        elif cmd == "6":
            print("Alla prossima avventura!")
            return True
        else:
            print("Opzione non valida.")


def demo():
    p = Player("Demo")
    e = Enemy("Lupo Selvatico", 12, 4, 8, 6)
    print("Eseguo demo rapida (automatica)...")
    fight_auto(p, e)


def fight_auto(player, enemy):
    print(f"Incontro! {enemy.name} appare (HP {enemy.hp})")
    while player.is_alive() and enemy.is_alive():
        dmg = player.attack(enemy)
        print(f"{player.name} attacca il {enemy.name} per {dmg} danni. (HP nemico {max(0, enemy.hp)})")
        if not enemy.is_alive():
            break
        edmg = random.randint(max(1, enemy.atk - 2), enemy.atk + 2)
        player.hp -= edmg
        print(f"{enemy.name} colpisce per {edmg} danni. (HP tuo {max(0, player.hp)})")
        time.sleep(0.2)
    if player.is_alive():
        print(f"Demo: hai sconfitto il {enemy.name}!")
    else:
        print("Demo: sei stato sconfitto...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Esegue una demo non interattiva")
    args = parser.parse_args()
    if args.demo:
        demo()
    else:
        name = input("Come ti chiami, avventuriero? ").strip() or "Eroe"
        player = Player(name)
        main_loop(player)
