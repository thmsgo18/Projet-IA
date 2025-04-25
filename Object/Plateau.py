# Plateau.py
import queue

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
        if orientation == "horizontal" and self.est_mur_horizontal_valide(x, y):
            for dy in (-1,0,1):
                self.matrice[x][y+dy] = Plateau.WALL
            return True
        if orientation == "vertical" and self.est_mur_vertical_valide(x, y):
            for dx in (-1,0,1):
                self.matrice[x+dx][y] = Plateau.WALL
            return True
        return False

    def chemin_existe(self, depart, ligne_obj):
        """BFS sur les cellules en sautant case-mur-case, détecte correctement WALL."""
        visited = set()
        q = queue.Queue()
        q.put(depart)
        while not q.empty():
            x,y = q.get()
            if x == ligne_obj:
                return True
            visited.add((x,y))
            for dx,dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                nx,ny = x+dx, y+dy
                if not (0 <= nx < len(self.matrice) and 0 <= ny < len(self.matrice)): continue
                if (nx,ny) in visited: continue
                # case intermédiaire : mur ?
                mx,my = (x+nx)//2, (y+ny)//2
                if self.matrice[mx][my] == Plateau.WALL: continue
                # la destination doit être une cellule vide ou un joueur
                if self.matrice[nx][ny] in (Plateau.CELL, "1", "2"):
                    q.put((nx,ny))
        return False