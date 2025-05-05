# Quoridor.py
import sys
from Object.Plateau import Plateau
from Object.Joueur import Joueur
from GameState import GameState

# Paramètres pour les différents niveaux d'IA
IA_LEVELS = {
    "facile": {
        "profondeur": 1,
        "epsilon": 0.4,
        "poids_avancer": 1,
        "poids_bloquer": 0.5,
        "poids_murs": 0.2
    },
    "moyen": {
        "profondeur": 2,
        "epsilon": 0.2,
        "poids_avancer": 1.2,
        "poids_bloquer": 0.8,
        "poids_murs": 0.3
    },
    "difficile": {
        "profondeur": 3,
        "epsilon": 0.1,
        "poids_avancer": 1.5,
        "poids_bloquer": 1,
        "poids_murs": 0.4
    }
}

class Quoridor:
    def __init__(self, ai_flags=None, ai_level="moyen"):
        """
        ai_flags: liste de bool [is_ai_joueur1, is_ai_joueur2]
        ai_level: niveau de difficulté de l'IA ("facile", "moyen", "difficile")
        """
        self.plateau = Plateau()
        max_idx = 2 * self.plateau.taille - 2  # 16 si taille=9
        mid    = self.plateau.taille - 1      #  8
        # instanciation des joueurs
        self.joueurs = [
            Joueur("1", (0,    mid), max_idx),
            Joueur("2", (max_idx, mid), 0)
        ]
        for j in self.joueurs:
            self.plateau.placer_joueur(j)
        self.tour = 0
        # par défaut, personne n'est IA
        self.ai_flags = ai_flags or [False, False]
        # niveau de l'IA
        self.ai_level = ai_level
        # niveaux spécifiques pour chaque IA (utilisé en mode IA vs IA)
        self.ai_levels = {0: ai_level, 1: ai_level}

    def afficher_plateau(self):
        self.plateau.afficher()
        for j in self.joueurs:
            print(f"Joueur {j.nom} : murs restants = {j.nb_murs}")
        print()

    def verifier_victoire(self):
        for j in self.joueurs:
            if j.position[0] == j.ligne_obj:
                return j.nom
        return None

    def jouer_tour(self):
        j = self.joueurs[self.tour]
        is_ai = self.ai_flags[self.tour]

        # Si IA, on choisit et applique automatiquement
        if is_ai:
            # Utiliser le niveau spécifique à cette IA
            current_ai_level = self.ai_levels.get(self.tour, self.ai_level)
            print(f"--- Tour du joueur {j.nom} (IA - {current_ai_level}) ---")
            state = GameState(self.plateau, self.joueurs, self.tour)
            
            # Récupérer les paramètres selon le niveau
            params = IA_LEVELS[current_ai_level]
            profondeur = params["profondeur"]
            epsilon_base = params["epsilon"]
            
            # Utiliser une valeur fixe pour epsilon, sans notion de phase
            epsilon = epsilon_base
            
            best_move = state.choix_coup(
                profondeur=profondeur,
                IA_index=self.tour,
                epsilon=epsilon
            )
            print("L'IA joue :", best_move)
            new_state = state.apply_move(best_move)
            self.plateau = new_state.plateau
            self.joueurs = new_state.joueurs
            self.tour = new_state.tour
            return

        # Sinon, interaction humaine
        print(f"--- Tour du joueur {j.nom} ---")
        choix = input("(d)éplacer, (m)ur, (q)uitter : ").strip().lower()
        if choix == "q":
            print("Au revoir !")
            sys.exit()
        if choix == "d":
            dir_map = {"h":(-2,0),"b":(2,0),"g":(0,-2),"d":(0,2)}
            d = input("direction (h/b/g/d) : ").strip().lower()
            if d not in dir_map:
                print("Direction invalide."); return
            dx,dy = dir_map[d]
            np = (j.position[0]+dx, j.position[1]+dy)
            if not j.deplacer(np, self.plateau):
                print("Déplacement invalide."); return
        elif choix == "m":
            if j.nb_murs==0:
                print("Plus de murs !"); return
            try:
                x = int(input("x mur (impair) : "))
                y = int(input("y mur (impair) : "))
            except ValueError:
                print("Coordonnées invalides."); return
            ori = input("orientation (h)orizontal/(v)ertical : ").strip().lower()
            if ori not in ("h","v"):
                print("Orientation invalide."); return
            if not self.plateau.placer_mur(y,x,ori):
                print("Placement invalide."); return
            if not all(self.plateau.chemin_existe(p.position,p.ligne_obj)
                       for p in self.joueurs):
                print("Bloque un chemin !"); return
            j.utiliser_mur()
        else:
            print("Action inconnue."); return

        # Tour suivant (humain)
        self.tour = (self.tour + 1) % len(self.joueurs)

if __name__ == "__main__":
    # Sélection du mode
    mode = None
    while mode not in ("1","2","3"):
        mode = input("Mode de jeu: 1) H vs H  2) H vs IA  3) IA vs IA : ").strip()
    
    # Définir les flags IA
    ai_flags = [False, False]
    if mode == "2":
        ai_flags[1] = True
        # Sélection du niveau d'IA pour l'adversaire
        level = None
        while level not in ("1", "2", "3"):
            level = input("Niveau de l'IA: 1) Facile  2) Moyen  3) Difficile : ").strip()
        ai_level = {
            "1": "facile",
            "2": "moyen",
            "3": "difficile"
        }[level]
    elif mode == "3":
        ai_flags = [True, True]
        # Sélection du niveau pour chaque IA
        level1 = None
        while level1 not in ("1", "2", "3"):
            level1 = input("Niveau de l'IA 1: 1) Facile  2) Moyen  3) Difficile : ").strip()
        level2 = None
        while level2 not in ("1", "2", "3"):
            level2 = input("Niveau de l'IA 2: 1) Facile  2) Moyen  3) Difficile : ").strip()
        
        # Créer un dictionnaire pour stocker les niveaux de chaque IA
        ai_levels = {
            0: {
                "1": "facile",
                "2": "moyen",
                "3": "difficile"
            }[level1],
            1: {
                "1": "facile",
                "2": "moyen",
                "3": "difficile"
            }[level2]
        }
        # Utiliser le niveau moyen comme niveau par défaut pour l'interface
        ai_level = "moyen"
    else:
        ai_level = "moyen"  # Valeur par défaut, ne sera pas utilisée

    # Créer le jeu
    jeu = Quoridor(ai_flags=ai_flags, ai_level=ai_level)
    
    # Si mode IA vs IA, stocker les niveaux spécifiques
    if mode == "3":
        jeu.ai_levels = ai_levels
    while True:
        jeu.afficher_plateau()
        if (g := jeu.verifier_victoire()) is not None:
            print(f"Le joueur {g} a gagné !")
            break
        jeu.jouer_tour()
