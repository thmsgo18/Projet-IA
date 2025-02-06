import queue

class Plateau:
    def __init__(self, taille=9):
        self.taille = taille  # Taille du plateau (9x9)
        self.matrice = [[" " for _ in range(2 * taille - 1)] for _ in range(2 * taille - 1)]
        self.murs = []  # Liste des murs placés (x, y, orientation)

        # Initialisation des cases de jeu
        for i in range(0, len(self.matrice), 2):
            for j in range(0, len(self.matrice), 2):
                self.matrice[i][j] = "o"  # Les cases de jeu

    def afficher(self):
        """Affiche le plateau avec les positions des murs."""
        # Affichage de l'entête des colonnes (positions impaires)
        print("X|Y=>", end="")
        for j in range(1, len(self.matrice[0]), 2):
            print(f" {j:2}", end="   ")
        print()  # Nouvelle ligne après l'entête des colonnes
        
        # Affichage des lignes du plateau avec les indices des murs
        for i in range(len(self.matrice)):
            if i % 2 == 1:  # Indice des lignes impaires
                print(f"{i:2}", end=" ")  # Affiche l'indice des lignes impaires
            else:
                print("   ", end=" ")  # Alignement pour les lignes paires
            
            # Affichage du contenu de la ligne
            for j in range(len(self.matrice[i])):
                print(self.matrice[i][j], end="  ")
            print()  # Nouvelle ligne après chaque ligne du plateau

    def placer_joueur(self, J):
        """Placement d'un joueur sur le plateau"""
        self.matrice[J.position[0]][J.position[1]] = J.nom

    def est_mur_valide(self, x, y, orientation):
        """Vérifie si un mur peut être placé à la position donnée."""
        # Vérifier si les coordonnées sont dans les limites
        if x < 0 or y < 0 or x >= len(self.matrice) or y >= len(self.matrice[0]):
            return False
        if not x%2 == 1 :
            return False

        # Vérifier si le mur est déjà placé
        if orientation == "horizontal":
            if self.matrice[x][y] == "-" or self.matrice[x][y + 1] == "-":
                return False
        elif orientation == "vertical":
            if self.matrice[x][y] == "|" or self.matrice[x + 1][y] == "|":
                return False

        # Si toutes les conditions sont respectées, le mur est valide
        return True

    def placer_mur(self, x, y, orientation):
        """Place un mur sur le plateau si c'est possible."""
        if not self.est_mur_valide(x, y, orientation):
            print("Placement de mur invalide.")
            return False

        # Placer le mur
        if orientation == "horizontal":
            self.matrice[x][y] = "-"
            self.matrice[x][y + 1] = "-"
        elif orientation == "vertical":
            self.matrice[x][y] = "|"
            self.matrice[x + 1][y] = "|"

        self.murs.append((x, y, orientation))
        return True
    
    def chemin_existe(self, position_depart, objectif):
        """Vérifie si un chemin existe entre la position de départ et l'objectif."""
        taille = self.taille
        visite = set()
        q = queue.Queue()
        q.put(position_depart)

        while not q.empty():
            x, y = q.get()
            if (x, y) == objectif:
                return True

            # Marquer la position comme visitée
            visite.add((x, y))

            # Explorer les directions (haut, bas, gauche, droite)
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 2 * taille - 1 and 0 <= ny < 2 * taille - 1:
                    if (nx, ny) not in visite and self.matrice[(x + nx) // 2][(y + ny) // 2] not in ["-", "|"]:
                        q.put((nx, ny))

        return False

