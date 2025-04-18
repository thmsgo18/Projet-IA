# Quoridor.py
from Object.Plateau import Plateau
from Object.Joueur import Joueur

class Quoridor:
    def __init__(self):
        self.plateau = Plateau()
        # indice maximal de la matrice (2*taille-2) et colonne centrale (taille-1)
        max_idx = 2 * self.plateau.taille - 2  # 16 si taille=9
        mid    = self.plateau.taille - 1      #  8
        # J1 en (0,8) visant la dernière ligne, J2 en (16,8) visant la première
        self.joueurs = [
            Joueur("1", (0,    mid), max_idx),
            Joueur("2", (max_idx, mid), 0)
        ]
        for j in self.joueurs:
            self.plateau.placer_joueur(j)
        self.tour = 0


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
        print(f"--- Tour du joueur {j.nom} ---")
        choix = input("(d)éplacer, (m)ur, (q)uitter : ").strip().lower()
        if choix == "q":
            print("Au revoir !")
            exit()
        if choix == "d":
            dir_map = {"h":(-2,0),"b":(2,0),"g":(0,-2),"d":(0,2)}
            d = input("direction (h/b/g/d) : ").strip().lower()
            if d not in dir_map:
                print("Direction invalide."); return
            dx,dy = dir_map[d]
            np = (j.position[0]+dx, j.position[1]+dy)
            if not j.deplacer(np, self.plateau):
                print("Déplacement invalide.")
                return
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
            # ne bloque pas les chemins ?
            if not all(self.plateau.chemin_existe(p.position,p.ligne_obj)
                       for p in self.joueurs):
                # rollback
                print("Bloque un chemin !"); return
            j.utiliser_mur()
        else:
            print("Action inconnue.")
            return

        self.tour = (self.tour+1) % len(self.joueurs)

if __name__ == "__main__":
    jeu = Quoridor()
    while True:
        jeu.afficher_plateau()
        if (g := jeu.verifier_victoire()) is not None:
            print(f"Le joueur {g} a gagné !")
            break
        jeu.jouer_tour()
