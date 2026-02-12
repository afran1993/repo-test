import random


def calculate_damage(attacker, defender, base=5, element=None):
    # base damage modified by attacker stats and defender defenses
    atk = base + attacker.stats.get('str', 5)
    defense = defender.stats.get('end', 3)
    dmg = max(1, atk - int(defense * 0.5) + random.randint(-2, 2))
    return dmg


def turn_based_fight(player, enemy, engine=None):
    print(f"Combat start: {player.name} vs {enemy.name}")
    # simple alternating turns
    turn = 0
    while player.is_alive() and enemy.is_alive():
        actor = player if turn % 2 == 0 else enemy
        target = enemy if actor is player else player
        if actor is player:
            # present choices
            print(player.describe())
            print(enemy.describe())
            print("Actions: (1)Attack  (2)Use Potion  (3)Flee")
            choice = input('-> ').strip()
            if choice == '1':
                dmg = calculate_damage(player, enemy)
                enemy.hp -= dmg
                print(f"You hit {enemy.name} for {dmg} dmg.")
            elif choice == '2':
                # simple potion
                pot = next((i for i in player.inventory if i.get('id')=='potion_small'), None)
                if pot:
                    heal = 12
                    player.hp = min(player.max_hp, player.hp + heal)
                    player.inventory.remove(pot)
                    print(f"You use a potion and heal {heal} HP.")
                else:
                    print("No potion.")
            elif choice == '3':
                if random.random() < 0.5:
                    print("You fled the fight.")
                    return False
                else:
                    print("Flee failed.")
            else:
                print("Invalid action, you lose your turn.")
        else:
            dmg = calculate_damage(enemy, player)
            player.hp -= dmg
            print(f"{enemy.name} hits you for {dmg} dmg.")
        turn += 1

    if player.is_alive():
        print(f"You defeated {enemy.name}!")
        return True
    else:
        print("You were defeated...")
        return False
