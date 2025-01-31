class Joueur:
    def __init__(self, nom, position, objectif, nb_murs=10):
        self.nom = nom
        self.position = position  # Position sous forme de tuple (x, y)
        self.objectif = objectif  # Ligne à atteindre
        self.nb_murs = nb_murs  # Nombre de murs restants

    def deplacer(self, nouvelle_position):
        """Met à jour la position du joueur."""
        self.position = nouvelle_position

    def utiliser_mur(self):
        """Décrémente le nombre de murs si possible."""
        if self.nb_murs > 0:
            self.nb_murs -= 1
            return True
        return False
