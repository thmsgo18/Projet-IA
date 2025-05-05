class Joueur:
    def __init__(self, nom, position, ligne_obj, nb_murs=10):
        self.nom = nom                 # "1" ou "2"
        self.position = position       # tuple (x,y)
        self.ligne_obj = ligne_obj     # ligne cible à atteindre
        self.nb_murs = nb_murs

    def deplacer(self, nouvelle_pos, plateau):
        x0, y0 = self.position
        x1, y1 = nouvelle_pos

        dim = len(plateau.matrice)
        if not (0 <= x1 < dim and 0 <= y1 < dim):
            # hors plateau → déplacement invalide
            return False

        # on ne gère que les pas de 2 dans un axe
        if not ((x0 == x1 and abs(y0-y1) == 2) or (y0 == y1 and abs(x0-x1) == 2)):
            return False

        # s'il y a un adversaire, on passe au saut
        if plateau.matrice[x1][y1] in ("1","2"):
            return self.tenter_saut(x0, y0, x1, y1, plateau)

        # sinon, saut droit sans adversaire : on bloque si mur au milieu
        mx, my = (x0+x1)//2, (y0+y1)//2
        if plateau.matrice[mx][my] == plateau.WALL:
            return False

        # case vide => on bouge
        if plateau.matrice[x1][y1] == plateau.CELL:
            plateau.matrice[x0][y0] = plateau.CELL
            self.position = (x1, y1)
            plateau.matrice[x1][y1] = self.nom
            return True

        return False

    def tenter_saut(self, x0, y0, x1, y1, plateau):
        # vérification de s'il y a un mur entre le joueur et l'adversaire
        mx, my = (x0 + x1) // 2, (y0 + y1) // 2
        if plateau.matrice[mx][my] == plateau.WALL:
            return False

        dx, dy = x1 - x0, y1 - y0
        taille = plateau.taille * 2 - 1

        # saut droit derrière l'adversaire
        bx, by = x1 + dx, y1 + dy
        if 0 <= bx < taille and 0 <= by < taille:
            # pas de mur entre (x1,y1) et (bx,by) ?
            if plateau.matrice[(x1 + bx) // 2][(y1 + by) // 2] != plateau.WALL \
                    and plateau.matrice[bx][by] == plateau.CELL:
                plateau.matrice[x0][y0] = plateau.CELL
                self.position = (bx, by)
                plateau.matrice[bx][by] = self.nom
                return True

        # si saut droit bloqué, on essaie les sauts diagonaux
        if dx != 0:
            diag_moves = [(0, -2), (0, 2)]
        else:
            diag_moves = [(-2, 0), (2, 0)]

        for sx, sy in diag_moves:
            cx, cy = x1 + sx, y1 + sy
            if not (0 <= cx < taille and 0 <= cy < taille):
                continue
            # pas de mur entre (x1,y1) et (cx,cy) ?
            if plateau.matrice[(x1 + cx) // 2][(y1 + cy) // 2] != plateau.WALL \
                    and plateau.matrice[cx][cy] == plateau.CELL:
                plateau.matrice[x0][y0] = plateau.CELL
                self.position = (cx, cy)
                plateau.matrice[cx][cy] = self.nom
                return True

        return False

    def utiliser_mur(self):
        if self.nb_murs>0:
            self.nb_murs -= 1
            return True
        return False

    def get_deplacements_possibles(self, plateau):
        possibles = []
        x0, y0 = self.position
        dim = len(plateau.matrice)

        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            x1, y1 = x0 + dx, y0 + dy
            if not (0 <= x1 < dim and 0 <= y1 < dim):
                continue
            mx, my = (x0 + x1)//2, (y0 + y1)//2
            if plateau.matrice[mx][my] == plateau.WALL:
                continue
            if plateau.matrice[x1][y1] == plateau.CELL:
                possibles.append((x1, y1))
        return possibles
