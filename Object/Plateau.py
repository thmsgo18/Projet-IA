# Plateau.py
import queue
from collections import deque


class Plateau:
    EMPTY = " "
    CELL = "o"
    WALL = "█"

    def __init__(self, taille=9):
        self.taille = taille
        dim = 2 * taille - 1
        # matrice carrée dim×dim
        self.matrice = [[Plateau.EMPTY for _ in range(dim)] for _ in range(dim)]
        # placer les cellules jouables
        for i in range(0, dim, 2):
            for j in range(0, dim, 2):
                self.matrice[i][j] = Plateau.CELL

    def afficher(self):
        # entêtes de colonnes
        print("    " + "".join(f"{j:>3}" for j in range(len(self.matrice))))
        for i, ligne in enumerate(self.matrice):
            print(f"{i:>3} ", end="")
            for case in ligne:
                print(f"{case:^3}", end="")
            print()

    def placer_joueur(self, joueur):
        x, y = joueur.position
        self.matrice[x][y] = joueur.nom

    def est_mur_horizontal_valide(self, x, y):
        dim = len(self.matrice)
        if 0 < x < dim and 1 <= y < dim-1:
            return all(self.matrice[x][y+dy] == Plateau.EMPTY for dy in (-1,0,1))
        return False

    def est_mur_vertical_valide(self, x, y):
        dim = len(self.matrice)
        if 1 <= x < dim-1 and 0 < y < dim:
            return all(self.matrice[x+dx][y] == Plateau.EMPTY for dx in (-1,0,1))
        return False

    def placer_mur(self, x, y, orientation):
        # coordonnées impaires
        if x % 2 == 0 or y % 2 == 0:
            return False
        if orientation == "h" and self.est_mur_horizontal_valide(x, y):
            for dy in (-1,0,1):
                self.matrice[x][y+dy] = Plateau.WALL
            return True
        if orientation == "v" and self.est_mur_vertical_valide(x, y):
            for dx in (-1,0,1):
                self.matrice[x+dx][y] = Plateau.WALL
            return True
        return False


    def chemin_existe(self, start: tuple[int,int], target_line: int) -> bool:
        """
        Vérifie s'il existe un chemin libre (sans murs) depuis `start`
        jusqu'à n'importe quelle cellule sur la ligne `target_line`.
        """
        visited = {start}
        q = deque([start])
        dim = len(self.matrice)

        while q:
            x, y = q.popleft()
            # Si on a atteint la ligne cible, il y a un chemin
            if x == target_line:
                return True

            # Explorer les 4 déplacements « cases » (pas de saut ici)
            for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                nx, ny = x + dx, y + dy
                # Hors plateau ?
                if not (0 <= nx < dim and 0 <= ny < dim):
                    continue

                # Vérifier le mur intermédiaire
                mx, my = (x + nx)//2, (y + ny)//2
                if self.matrice[mx][my] == Plateau.WALL:
                    continue

                # Si jamais visité, on ajoute à la file
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny))

        # File épuisée, pas de chemin
        return False