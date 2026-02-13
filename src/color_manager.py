"""ANSI color codes for terminal text formatting."""

# ANSI color codes
COLORS = {
    'RESET': '\033[0m',
    'BRIGHT_CYAN': '\033[96m',
    'BRIGHT_GREEN': '\033[92m',
    'BRIGHT_RED': '\033[91m',
    'BRIGHT_YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'GREEN': '\033[32m',
    'RED': '\033[31m',
    'YELLOW': '\033[33m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
}


def colored(text, color_name):
    """Return text with ANSI color codes."""
    color = COLORS.get(color_name, '')
    return f"{color}{text}{COLORS['RESET']}"


def format_status(player, i18n=None):
    """Format player status with colors and translations."""
    # Traduzione dei termini
    if i18n:
        gold_label = i18n.t('gold')
        potions_label = i18n.t('potions')
    else:
        gold_label = 'Oro' if getattr(player, 'language', 'it') == 'it' else 'Gold'
        potions_label = 'Pozioni' if getattr(player, 'language', 'it') == 'it' else 'Potions'
    
    # Calcola i totali
    total_atk = player.get_total_atk()
    total_dex = player.get_total_dex()
    total_max_hp = player.get_total_max_hp()
    total_potions = sum(player.potions.values())
    
    # Formatta il nome - CYAN
    name_part = colored(f"{player.name}", 'BRIGHT_CYAN')
    
    # Formatta il livello - BLU
    level_part = colored(f"LV {player.level}", 'BLUE')
    
    # Formatta l'HP - VERDE/ROSSO
    hp_part = colored(f"{player.hp}", 'BRIGHT_GREEN') + "/" + colored(f"{total_max_hp}", 'BRIGHT_RED')
    
    # Formatta ATK e DEX - GIALLO
    atk_part = colored(f"ATK {total_atk}", 'BRIGHT_YELLOW')
    dex_part = colored(f"DEX {total_dex}", 'BRIGHT_YELLOW')
    
    # Formatta XP - VERDE/ROSSO
    xp_part = colored(f"{player.xp}", 'BRIGHT_GREEN') + "/" + colored(f"{player.level*12}", 'BRIGHT_RED')
    
    # Formatta Gold - GIALLO
    gold_part = colored(f"{gold_label} {player.gold}", 'BRIGHT_YELLOW')
    
    # Formatta Potions - VERDE
    potions_part = colored(f"🧪{potions_label} {total_potions}", 'BRIGHT_GREEN')
    
    # Formatta arma - DEFAULT
    weapon_str = f" [" + (f"{player.equipped_weapon['name']}" if player.equipped_weapon else "Pugno") + "]"
    
    # Formatta accessori - DEFAULT (con separazione migliore)
    acc_parts = []
    for slot, acc in player.accessories.items():
        if acc:
            acc_parts.append(acc['name'])
    
    acc_str = ""
    if acc_parts:
        acc_str = " (" + ", ".join(acc_parts) + ")"
    
    # Assembla lo status
    status = f"{name_part} - {level_part}  HP {hp_part}  {atk_part}  {dex_part}  XP {xp_part}  {gold_part}  {potions_part}{weapon_str}{acc_str}"
    
    return status
