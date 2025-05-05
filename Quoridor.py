import sys
from Object.Plateau import Plateau
from Object.Joueur import Joueur
from GameState import GameState

# Définition des parametres des différents niveaux d'IA
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
    """
    Classe représentant le jeu Quoridor
    """
    def __init__(self, ai_flags=None, ai_level="moyen"):
        """
        Fonction d'initialisation de la classe
        """
        self.plateau = Plateau()
        max_idx = 2 * self.plateau.taille - 2
        mid    = self.plateau.taille - 1
        # liste des joueurs
        self.joueurs = [
            Joueur("1", (0,    mid), max_idx),
            Joueur("2", (max_idx, mid), 0)
        ]
        for j in self.joueurs:
            self.plateau.placer_joueur(j)
        self.tour = 0
        self.ai_flags = ai_flags or [False, False]
        self.ai_level = ai_level
        self.ai_levels = {0: ai_level, 1: ai_level}

    def afficher_plateau(self):
        """
        Fonction d'affichage du plateau.
        """
        self.plateau.afficher()
        for j in self.joueurs:
            print(f"Joueur {j.nom} : murs restants = {j.nb_murs}")
        print()

    def verifier_victoire(self):
        """
        Fonction de vérification de la victoire
        """
        for j in self.joueurs:
            if j.position[0] == j.ligne_obj:
                return j.nom
        return None

    def jouer_tour(self):
        """
        Fonction permettant de jouer un tour
        """
        j = self.joueurs[self.tour]
        is_ai = self.ai_flags[self.tour]

        if is_ai:
            # Dans le cas où le joueur est une IA
            current_ai_level = self.ai_levels.get(self.tour, self.ai_level)
            print(f"--- Tour du joueur {j.nom} (IA - {current_ai_level}) ---")
            state = GameState(self.plateau, self.joueurs, self.tour)
            
            params = IA_LEVELS[current_ai_level]
            profondeur = params["profondeur"]
            epsilon_base = params["epsilon"]
            
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

        # Dans le cas ou le jour est un humain
        print(f"--- Tour du joueur {j.nom} ---")
        choix = input("(d)éplacer, (m)ur, (q)uitter : ").strip().lower()
        # Action réalisé en fonction de la saisie de l'utilisateur
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

        self.tour = (self.tour + 1) % len(self.joueurs)

if __name__ == "__main__":
    # Lancement du programme
    mode = None
    # Choix du mode de jeux
    while mode not in ("1","2","3"):
        mode = input("Mode de jeu: 1) H vs H  2) H vs IA  3) IA vs IA : ").strip()
    
    ai_flags = [False, False]
    if mode == "2":
        # Condition permettant de redemandé une saisie à l'utilisateur pour choisir le niveau de l'IA
        ai_flags[1] = True
        level = None
        while level not in ("1", "2", "3"):
            level = input("Niveau de l'IA: 1) Facile  2) Moyen  3) Difficile : ").strip()
        ai_level = {
            "1": "facile",
            "2": "moyen",
            "3": "difficile"
        }[level]
    elif mode == "3":
        # Condition permettant de redemandé une saisie à l'utilisateur pour choisir le niveau des IAs
        ai_flags = [True, True]
        level1 = None
        while level1 not in ("1", "2", "3"):
            level1 = input("Niveau de l'IA 1: 1) Facile  2) Moyen  3) Difficile : ").strip()
        level2 = None
        while level2 not in ("1", "2", "3"):
            level2 = input("Niveau de l'IA 2: 1) Facile  2) Moyen  3) Difficile : ").strip()
        
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
        ai_level = "moyen"
    else:
        ai_level = "moyen"

    # Création d'une instance de la classe Quoridor
    jeu = Quoridor(ai_flags=ai_flags, ai_level=ai_level)
    
    if mode == "3":
        jeu.ai_levels = ai_levels
    while True:
        jeu.afficher_plateau()
        if (g := jeu.verifier_victoire()) is not None:
            print(f"Le joueur {g} a gagné !")
            break
        jeu.jouer_tour()
