class Plateau :
    def __init__(self, taille=9):
        self.taille = taille
        self.matrice = [[" " for _ in range(2 * taille - 1)] for _ in range(2 * taille - 1)]
        # Les cases d'indice impaires représenterons les cases jouables.
        for i in range(0, 2 * taille -1, 2):
            for j in range(0, 2 * taille -1, 2):
                self.matrice[i][j] = "o"
        # Les cases d'indice paires représenteront les emplacements pour les murs

    def afficher(self):
        for ligne in self.matrice:
            print("".join(ligne))



#plateau = Plateau()
#plateau.afficher()