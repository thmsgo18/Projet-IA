class Joueur:
    def __init__(self, nom, position, objectif, nb_murs=10):
        self.nom = nom
        self.position = position  # Position sous forme de tuple (x, y)
        self.objectif = objectif  # Ligne à atteindre
        self.nb_murs = nb_murs  # Nombre de murs restants

    def deplacer(self, nouvelle_position, plateau):
        x_actuel, y_actuel = self.position
        x_nouveau, y_nouveau = nouvelle_position
        
        # Vérifier si le déplacement est horizontal
        if x_actuel == x_nouveau:
            y_mur = min(y_actuel, y_nouveau) + 1
            if plateau.matrice[x_actuel][y_mur] == "|":
                print("Déplacement impossible : un mur bloque le passage.")
                return False
        
        # Vérifier si le déplacement est vertical
        elif y_actuel == y_nouveau:
            x_mur = min(x_actuel, x_nouveau) + 1
            if plateau.matrice[x_mur][y_actuel] == "-":
                print("Déplacement impossible : un mur bloque le passage.")
                return False
        
        # Supprimer l'ancienne position sur le plateau
        plateau.matrice[x_actuel][y_actuel] = " "

        # Mettre à jour la position du joueur
        self.position = nouvelle_position
        plateau.matrice[x_nouveau][y_nouveau] = "o"

        return True

    def utiliser_mur(self):
        """Décrémente le nombre de murs si possible."""
        if self.nb_murs > 0:
            self.nb_murs -= 1
            return True
        return False
