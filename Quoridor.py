# Quoridor.py
import sys
from Object.Plateau import Plateau
from Object.Joueur import Joueur
from GameState import GameState

PROFONDEUR = 2     # ou 2, 4… selon le temps de calcul que tu acceptes

class Quoridor:
    def __init__(self, ai_flags=None):
        """
        ai_flags: liste de bool [is_ai_joueur1, is_ai_joueur2]
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
            print(f"--- Tour du joueur {j.nom} (IA) ---")
            state = GameState(self.plateau, self.joueurs, self.tour)
            best_move = state.choix_coup(
                profondeur=PROFONDEUR,
                IA_index=self.tour,
                epsilon=0.3,
                temperature=0.5
            )
            print("L'IA joue :", best_move)
            new_state = state.apply_move(best_move)
            self.plateau = new_state.plateau
            self.joueurs = new_state.joueurs
            self.tour = new_state.tour
            return

        # Sinon, interaction humaine
        print(f"--- Tour du joueur {j.nom} ---")
        choix = input("(d)éplacer, (m)ur, (i)A, (q)uitter : ").strip().lower()
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
            ori = input("orientation (horizontal/vertical) : ").strip().lower()
            if ori not in ("horizontal","vertical"):
                print("Orientation invalide."); return
            if not self.plateau.placer_mur(x,y,ori):
                print("Placement invalide."); return
            if not all(self.plateau.chemin_existe(p.position,p.ligne_obj)
                       for p in self.joueurs):
                print("Bloque un chemin !"); return
            j.utiliser_mur()
        elif choix == "i":
            # IA ponctuelle
            state = GameState(self.plateau, self.joueurs, self.tour)
            best_move = state.choix_coup(
                profondeur=PROFONDEUR,
                IA_index=self.tour,
                epsilon=0.3,
                temperature=0.5
            )
            print("L'IA joue :", best_move)
            new_state = state.apply_move(best_move)
            self.plateau = new_state.plateau
            self.joueurs = new_state.joueurs
            self.tour = new_state.tour
            return
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
    elif mode == "3":
        ai_flags = [True, True]

    jeu = Quoridor(ai_flags=ai_flags)
    while True:
        jeu.afficher_plateau()
        if (g := jeu.verifier_victoire()) is not None:
            print(f"Le joueur {g} a gagné !")
            break
        jeu.jouer_tour()
