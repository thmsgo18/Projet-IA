from Object.Joueur import Joueur
from Object.Plateau import Plateau

class Quoridor:
    def __init__(self):
        self.plateau = Plateau()
        self.joueurs = [
            Joueur("1", (0, 8),8,10 ),
            Joueur("2", (16, 8), 0,10),
        ]
        # Placement des joueurs sur le plateau
        for joueur in self.joueurs:
            self.plateau.placer_joueur(joueur)
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
            direction = input("Direction (haut (h), bas (b), gauche (g), droite (d)) : ").strip().lower()

            # Calcul de la nouvelle position
            nouvelle_position = self.calculer_nouvelle_position(joueur.position, direction)

            # Vérifier la validité de la position
            if nouvelle_position and self.position_valide(nouvelle_position):
                # Supprimer l'ancienne position du joueur
                self.plateau.matrice[joueur.position[0]][joueur.position[1]] = "o"
                # Mettre à jour la nouvelle position et la placer sur le plateau
                joueur.deplacer(nouvelle_position)
                self.plateau.placer_joueur(joueur)
            else:
                print("Déplacement invalide.")
        
        elif action == "m":
            # Logique existante pour placer les murs
            x = int(input("Coordonnée X du mur : "))
            y = int(input("Coordonnée Y du mur : "))
            orientation = input("Orientation (horizontal/vertical) : ")

            if joueur.utiliser_mur() and self.plateau.placer_mur(x, y, orientation):
                if all(self.plateau.chemin_existe(j.position, (j.objectif, j.position[1])) for j in self.joueurs):
                    print("Mur placé avec succès.")
                else:
                    print("Chemin bloqué, placement annulé.")
                    self.plateau.matrice[x][y] = " "
            else:
                print("Placement de mur invalide.")

        self.tour_actuel = (self.tour_actuel + 1) % 2  # Changer de joueur

    def calculer_nouvelle_position(self, position_actuelle, direction):
        """Retourne la nouvelle position basée sur la direction choisie."""
        x, y = position_actuelle
        if direction == "avant":
            return (x - 2, y)  # Vers le haut
        elif direction == "arrière":
            return (x + 2, y)  # Vers le bas
        elif direction == "gauche":
            return (x, y - 2)  # Vers la gauche
        elif direction == "droite":
            return (x, y + 2)  # Vers la droite
        else:
            return None  # Direction invalide

    def position_valide(self, position):
        """Vérifie si la position donnée est valide sur le plateau."""
        x, y = position
        if 0 <= x < len(self.plateau.matrice) and 0 <= y < len(self.plateau.matrice[0]) and x % 2 == 0 and y % 2 == 0:
            # Vérifie si la case est libre (pas de mur ni d'autre joueur)
            return self.plateau.matrice[x][y] == "o"
        return False
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
