from Object.Joueur import Joueur
from Object.Plateau import Plateau

class Quoridor:
    def __init__(self):
        self.plateau = Plateau()
        self.joueurs = [
            Joueur("Joueur 1", (0, 4),8,10 ),
             Joueur("Joueur 2", (8, 4), 0,10),
        ]   
        self.tour_actuel = 0  # Indice du joueur dont c'est le tour

    def afficher_plateau(self):
        """Affiche le plateau actuel."""
        self.plateau.afficher()

    def verifier_victoire(self):
        """Vérifie si un joueur a gagné."""
        for joueur in self.joueurs:
            if joueur.position[0] == joueur.objectif:
                return joueur.nom
        return None

    def tour_de_jeu(self):
        """Gère le tour du joueur actif."""
        joueur = self.joueurs[self.tour_actuel]
        print(f"Tour de {joueur.nom}")
        
        action = input("Déplacer (d) ou Placer mur (m) ? ")
        
        if action == "d":
            # Déplacer le joueur
            nouvelle_position = (int(input("Nouvelle ligne : ")), int(input("Nouvelle colonne : ")))
            joueur.deplacer(nouvelle_position)
        
        elif action == "m":
            # Placer un mur
            x = int(input("Coordonnée X du mur : "))
            y = int(input("Coordonnée Y du mur : "))
            orientation = input("Orientation (horizontal/vertical) : ")
            
            if joueur.utiliser_mur() and self.plateau.placer_mur(x, y, orientation):
                if all(self.plateau.chemin_existe(j.position, (j.objectif, j.position[1])) for j in self.joueurs):
                    joueur.nb_murs -= 1
                    print("Mur placé avec succès.")
                else:
                    print("Chemin bloqué, placement annulé.")
                    self.plateau.matrice[x][y] = " "
            else:
                print("Placement de mur invalide.")
        
        self.tour_actuel = (self.tour_actuel + 1) % 2  # Changer de joueur


# Création et exécution du jeu
jeu = Quoridor()
jeu.afficher_plateau()

while True:
    gagnant = jeu.verifier_victoire()
    if gagnant:
        print(f"{gagnant} a gagné !")
        break
    jeu.tour_de_jeu()
    jeu.afficher_plateau()
