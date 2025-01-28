class Joueur:
    def __init__(self, nom, position, objectif, nbr_murs=10):
        self.nom = nom
        self.position = position
        self.objectif = objectif
        self.nbr_murs = nbr_murs

    def deplacer(self, nouvelle_position):
        self.position = nouvelle_position
    
    def utiliser_mur(self):
        if self.nbr_murs > 0:
            self.nbr_murs -= 1
            return True
        return True

