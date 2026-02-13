"""Story progress tracking and management."""


class StoryManager:
    """Gestisce il sistema di storia principale del gioco."""
    
    def __init__(self, player):
        self.player = player
        # Story state is stored in player object for persistence
        # player.story_progress, player.story_stage, player.completed_acts, player.postgame
    
    def initialize_story(self):
        """Inizializza la storia per un nuovo giocatore."""
        self.player.story_progress = "act_1_awakening"
        self.player.story_stage = 0
        self.player.completed_acts = []
        if not hasattr(self.player, 'skills'):
            self.player.skills = {
                "swimming": False,
                "diving": False,
                "climbing": False,
                "pickpocketing": False,
                "stealth": False,
                "healing": False,
                "magic": False,
                "crafting": False,
            }
        if not hasattr(self.player, 'dialogues_completed'):
            self.player.dialogues_completed = []
        if not hasattr(self.player, 'dialogue_choices'):
            self.player.dialogue_choices = {}


def teach_skill(player, skill_name):
    """Insegna una nuova abilità al giocatore."""
    if not hasattr(player, 'skills'):
        player.skills = {
            "swimming": False, "diving": False, "climbing": False,
            "pickpocketing": False, "stealth": False, "healing": False,
            "magic": False, "crafting": False,
        }
    
    if skill_name not in player.skills:
        return False, f"Abilità '{skill_name}' non riconosciuta."
    
    if player.skills[skill_name]:
        return False, f"Conosci già '{skill_name}'!"
    
    player.skills[skill_name] = True
    
    skill_messages = {
        "swimming": "✦ HAI IMPARATO A NUOTARE! ✦\nOra puoi accedere alle lagune e alle rive dell'acqua.",
        "diving": "✦ HAI IMPARATO L'IMMERSIONE SUBACQUEA! ✦\nOra puoi esplorare le caverne sommerse.",
        "climbing": "✦ HAI IMPARATO AD ARRAMPICARTI! ✦\nOra puoi scalare montagne e alberi.",
        "pickpocketing": "✦ HAI IMPARATO L'ARTE DEL FURTO! ✦\nOra puoi rubare negli insediamenti.",
        "stealth": "✦ HAI IMPARATO LA FURTIVITÀ! ✦\nOra puoi muoverti senza essere notato.",
        "healing": "✦ HAI IMPARATO LA GUARIGIONE! ✦\nOra puoi curare le tue ferite più efficacemente.",
        "magic": "✦ HAI IMPARATO LA MAGIA! ✦\nOra puoi lanciare incantesimi in battaglia.",
        "crafting": "✦ HAI IMPARATO L'ARTIGIANATO! ✦\nOra puoi creare oggetti dai materiali.",
    }
    
    return True, skill_messages.get(skill_name, f"Hai imparato {skill_name}!")


def has_skill(player, skill_name):
    """Controlla se il giocatore possiede un'abilità."""
    if not hasattr(player, 'skills'):
        return False
    return player.skills.get(skill_name, False)


def get_available_skills(player):
    """Ritorna una lista di abilità non ancora imparate."""
    if not hasattr(player, 'skills'):
        return []
    return [skill for skill, learned in player.skills.items() if not learned]


def get_learned_skills(player):
    """Ritorna una lista di abilità già imparate."""
    if not hasattr(player, 'skills'):
        return []
    return [skill for skill, learned in player.skills.items() if learned]


def check_location_access(player, location_id, location_element):
    """Controlla se il giocatore ha accesso a una location in base alle abilità."""
    access_requirements = {
        "lagoon": {"skill": "swimming", "message": "Non sai ancora nuotare! Devi imparare prima."},
        "underwater_cave": {"skill": "diving", "message": "Non sai ancora tuffarti sott'acqua! Devi imparare a nuotare e poi ad immergerti."},
        "summit": {"skill": "climbing", "message": "Non sai ancora arrampicarti! Devi imparare prima."},
        "sky_temple": {"skill": "climbing", "message": "Hai bisogno di saper arrampicarti per raggiungere il tempio."},
    }
    
    if location_id in access_requirements:
        required_skill = access_requirements[location_id]["skill"]
        if not has_skill(player, required_skill):
            return False, access_requirements[location_id]["message"]
    
    return True, None


def check_story_milestone(player, location_id):
    """Controlla se c'è una milestone di storia quando arriva in una location."""
    # TODO: implementare milestones basate su location_id
    return None


def get_story_status(player):
    """Ritorna lo status della storia principale."""
    if not hasattr(player, 'story_progress'):
        return "Inizio dell'avventura"
    if not hasattr(player, 'story_stage'):
        player.story_stage = 0
    return f"{player.story_progress} - Stage {player.story_stage}"


def get_boss_for_location(location_id):
    """Ritorna il boss di una location, se esiste."""
    # TODO: implementare ricerca boss da dati
    return None


def get_current_main_quest(player):
    """Ritorna la quest principale corrente."""
    # TODO: implementare ricerca quest corrente
    return None


def update_story_progress(player):
    """Aggiorna il progresso della storia dopo aver sconfitto un boss."""
    # TODO: implementare aggiornamento storia
    pass
