import queue
import math
import random
import hashlib
from Object.Plateau import Plateau
from Object.Joueur import Joueur

TRANSPOSITION_TABLE = {}

class GameState:
    # classe permettant de gérer toute la partie IA du projet
    def __init__(self, plateau: Plateau, joueurs: list[Joueur], tour: int):
        """
        Fonction d'initialisation de la classe.
        """
        self.plateau = plateau
        self.joueurs = joueurs
        self.tour = tour
        self._hash = None

    def get_hash(self) -> str:
        """
        Fonction permettant de gérer plus facilement la mémoire de l'état du jeu
        Aide de ChatGPT
        """
        if self._hash is not None:
            return self._hash
            
        state_str = ""
        for row in self.plateau.matrice:
            state_str += ''.join(str(cell) for cell in row)
        for j in self.joueurs:
            state_str += f"{j.position[0]},{j.position[1]},{j.nb_murs}"
        state_str += str(self.tour)
        
        self._hash = hashlib.md5(state_str.encode()).hexdigest()
        return self._hash

    def clone(self) -> "GameState":
        """
        Fonction permettant de clonner l'état du jeu
        Aide de ChatGPT
        """
        newPlateau = Plateau(self.plateau.taille)
        dim = len(self.plateau.matrice)
        for i in range(dim):
            for j in range(dim):
                newPlateau.matrice[i][j] = self.plateau.matrice[i][j]

        newJoueurs = [Joueur(p.nom, p.position, p.ligne_obj, p.nb_murs) for p in self.joueurs]
        for j in newJoueurs:
            newPlateau.placer_joueur(j)

        return GameState(newPlateau, newJoueurs, self.tour)

    def _get_legal_moves_deplacement(self, joueur, x0, y0, dim) -> list:
        """
        Fonction permettant d'avoir la liste de tous les deplacements autorisés
        """
        moves = []
        # Liste de toutes les directions possibles.
        directions = [(-2,0), (2,0), (0,-2), (0,2)]
        
        for dx, dy in directions:
            # On boucle sur la liste des directions pour les tester.
            x1, y1 = x0 + dx, y0 + dy
            
            if not (0 <= x1 < dim and 0 <= y1 < dim):
                # verification que l'adresse de destination est sur le plateau.
                continue
            
            mx, my = (x0 + x1)//2, (y0 + y1)//2
            if self.plateau.matrice[mx][my] == Plateau.WALL:
                # verification de la présense de murs entre la position de débat et d'arrivée
                continue
            
            occupied = False
            for p in self.joueurs:
                # On vérifie que la case de destination est libre
                if p.position == (x1, y1):
                    occupied = True
                    break
                    
            if occupied:
                # Si la case de destination est occupée, on vérifie que l'on peu sauter par dessus l'adversaire.
                moves.extend(self._verifier_saut(x1, y1, dx, dy, dim))
            else:
                # Si le déplacement respect toutes les contraintes on l'ajoute à la liste de coups légaux que l'on va retourner.
                moves.append(("move", (x1, y1)))
                
        return moves
    
    def _verifier_saut(self, x1, y1, dx, dy, dim) -> list:
        """
        Fonction permettant de verifier que le saut au dessus d'un adversaire est possible.
        """
        moves = []
        x2, y2 = x1 + dx, y1 + dy
        
        if 0 <= x2 < dim and 0 <= y2 < dim:
            mx2, my2 = (x1 + x2)//2, (y1 + y2)//2
            if self.plateau.matrice[mx2][my2] != Plateau.WALL:
                if not any(p.position == (x2, y2) for p in self.joueurs):
                    moves.append(("move", (x2, y2)))
        return moves
    
    def _get_wall_positions(self, adversaire, dim) -> list:
        """
        Fonction permettant de retourner la liste des coordonnées intéressantes pour placer des murs sur le plateau
        """
        wall_positions = []
        # Position du joueur adverse afin de savoir où il est et donc de le bloquer.
        px, py = adversaire.position
        
        # Ici on définit la direction dans laquelle va le joueur adverse
        direction = -1 if adversaire.ligne_obj == 0 else 1
        front_x = px + direction * 2
        
        # On ajout des murs devant l'adversaire (dans le sens de sa progression)
        if 1 <= front_x < dim-1:
            for offset in [-2, 0, 2]:
                wx, wy = front_x, py + offset
                if 1 <= wy < dim-1 and wx % 2 == 1 and wy % 2 == 1:
                    wall_positions.append((wx, wy))
        
        # On place des murs autour de l'adversaire.
        for i in range(-3, 4, 2):
            for j in range(-3, 4, 2):
                wx, wy = px + i, py + j
                if 1 <= wx < dim-1 and 1 <= wy < dim-1 and wx % 2 == 1 and wy % 2 == 1:
                    wall_positions.append((wx, wy))
        
        # Ici on limite le nombre de placement de murs dans la liste des proposions. Cela permet d'éviter trop de calcule
        max_walls = 18
        if len(wall_positions) > max_walls:
            wall_positions = wall_positions[:max_walls]
        
        return wall_positions
    
    def _verifier_placement_mur(self, x, y, orientation, adversaire, d_adversaire) -> tuple:
        """
        Cette fonction permet de vérifier le placement d'un mur ainsi que son aspect stratégique.
        """
        # Dans ces deux tests nous vérifions s'il y'a un chevaugement de mur ou pas
        if orientation == "h":
            if (self.plateau.matrice[x][y-1] == Plateau.WALL or 
                self.plateau.matrice[x][y+1] == Plateau.WALL):
                return (False, None)
        else:
            if (self.plateau.matrice[x-1][y] == Plateau.WALL or 
                self.plateau.matrice[x+1][y] == Plateau.WALL):
                return (False, None)

        # Nous faisons une copie de l'état de la partie.
        s2 = self.clone()

        # Dans cette partie nous faisons une simulation du placement du mur
        if not s2.plateau.placer_mur(x, y, orientation):
            return (False, None)
        
        # Ici nous allons vérifier que les deux joueurs ont encore un chemin vers leur ligne d'arrivée
        if all(s2.plateau.chemin_existe(p.position, p.ligne_obj) for p in s2.joueurs):
            # Dans cette partie nous vérifions l'éfficacité du placement du mur
            new_d_adv = s2.bfs(s2.plateau, adversaire.position, adversaire.ligne_obj)
            
            if new_d_adv > d_adversaire:
                # On retiens ce positionnement de mur car la distance pour finir la partie pour l'adversaire a augmenté
                return (True, ("wall", x, y, orientation))
            
            elif new_d_adv == d_adversaire and random.random() < 0.3:
                # Distance vers l'arrivée inchangée pour l'adversaire mais pour plus de diversité selon la valeur du random nous gardons ce placement.
                return (True, ("wall", x, y, orientation))
            
        return (False, None)
    
    def get_legal_moves(self) -> list:
        """
        Fonction retournant la liste des coups possibles à jouer.
        """
        # Initialisation et récupération des informations nécessaires pour la fonction
        joueur = self.joueurs[self.tour] # Le joueur
        x0, y0 = joueur.position # la postion du joueur
        dim = len(self.plateau.matrice) # Les dimensions du plateau
        adversaire = self.joueurs[1 - self.tour] # l'adversaire
        
        moves = self._get_legal_moves_deplacement(joueur, x0, y0, dim)
        
        if joueur.nb_murs > 0:
            # Si le joueur a encore des murs en stock nous allons lister la position des murs possible et interessant à jouer
            d_moi = self.bfs(self.plateau, joueur.position, joueur.ligne_obj)
            d_adversaire = self.bfs(self.plateau, adversaire.position, adversaire.ligne_obj)
            
            # liste des positions de murs possibles à placé et stratégique.
            wall_positions = self._get_wall_positions(adversaire, dim)

            # verification de la validité du mur
            for x, y in wall_positions:
                for orientation in ["h", "v"]:
                    valide, coup = self._verifier_placement_mur(x, y, orientation, adversaire, d_adversaire)
                    if valide:
                        moves.append(coup)
        
        move_moves = [m for m in moves if m[0] == "move"] # liste des déplacements interessants.
        wall_moves = [m for m in moves if m[0] == "wall"] # liste des placements interessants.
        
        return move_moves + wall_moves
    
    def calculer_chemin(self, plateau: Plateau, depart: tuple, arrivee: int) -> list:
        """
        Fonction permettant de retourner le chemin entre un joueur et sa ligne d'arrivée. Nous utilisons un BFS.
        """
        visited = {depart}
        q = queue.Queue()
        q.put((depart, [depart]))
        dim = len(plateau.matrice)

        while not q.empty():
            (x, y), path = q.get()
            if x == arrivee:
                return path
            for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < dim and 0 <= ny < dim):
                    continue
                if (nx, ny) in visited:
                    continue
                mx, my = (x + nx)//2, (y + ny)//2
                if plateau.matrice[mx][my] == Plateau.WALL:
                    continue
                visited.add((nx, ny))
                q.put(((nx, ny), path + [(nx, ny)]))
        return []

    def apply_move(self, move: tuple) -> "GameState":
        """
        Cette fonction permet d'appliquer un coup sur le plateau.
        """
        nv = self.clone()
        tour = nv.tour
        joueur = nv.joueurs[tour]

        if move[0] == "move":
            _, (x, y) = move
            joueur.deplacer((x, y), nv.plateau)
        elif move[0] == "wall":
            _, x, y, ori = move
            nv.plateau.placer_mur(x, y, ori)
            joueur.utiliser_mur()
        else:
            raise ValueError(f"Coup inconnu: {move}")

        nv.tour = 1 - tour
        return nv

    def evaluer(self, IA_index: int, poids_avancer=1.2, poids_bloquer=0.8, poids_murs=0.1, 
               poids_avance=0.5) -> float:
        """
        Cette fonction permet d'evaluer un etat de jeu.
        """
        moi = self.joueurs[IA_index]
        adversaire = self.joueurs[1 - IA_index]
        
        d_moi = self.bfs(self.plateau, moi.position, moi.ligne_obj) # distance du joueur à la ligne d'arrivée
        d_adversaire = self.bfs(self.plateau, adversaire.position, adversaire.ligne_obj) # distance de l'adversaire à la ligne d'arrivée
        
        score_avancer = -poids_avancer * d_moi # score de l'avancé du joueur
        
        score_bloquer = poids_bloquer * d_adversaire # score de l'avancé de l'adversaire
        
        importance_murs = poids_murs # poids accordé à l'importance de placer un mur.
        if d_moi <= 4 or d_adversaire <= 4:
            importance_murs = poids_murs * 2 # Changement de la valeur de poids de mur quand la fin de partie approche
        score_murs = importance_murs * (moi.nb_murs - adversaire.nb_murs)
        
        avantage_relatif = d_adversaire - d_moi # Comparaison de l'avancement entre les deux joueurs.
        bonus_avance = poids_avance * avantage_relatif
        
        return score_avancer + score_bloquer + score_murs + bonus_avance

    def bfs(self, plateau: Plateau, start: tuple, target_line: int) -> float:
        """
        Fonction permettant de retourner la distance entre un joueur et sa ligne d'arrivée. Si pas de chemin trouvé la fonction renvoie la valeur infini
        """
        visited = {start}
        q = queue.Queue()
        q.put((start, 0))
        dim = len(plateau.matrice)

        while not q.empty():
            (x, y), dist = q.get()
            if x == target_line:
                return dist
            for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                nx, ny = x + dx, y + dy
                if not (0 <= nx < dim and 0 <= ny < dim):
                    continue
                if (nx, ny) in visited:
                    continue
                mx, my = (x + nx)//2, (y + ny)//2
                if plateau.matrice[mx][my] == Plateau.WALL:
                    continue
                visited.add((nx, ny))
                q.put(((nx, ny), dist+1))
        return math.inf

    def is_terminal(self) -> bool:
        """
        Fonction permettant de savoir si une partie est finit.
        """
        joueur_actuel = self.joueurs[self.tour]
        return joueur_actuel.position[0] == joueur_actuel.ligne_obj

    def get_winner(self) -> str:
        """
        Fonction permettant de savoir quel joueur a gagné.
        """
        for j in self.joueurs:
            if j.position[0] == j.ligne_obj:
                return j.nom
        return None

    """
    # V1 algo Min Max :

    def minMax(self, profondeur: int, IA_index: int):
        if self.is_terminal():
            winner = self.get_winner()
            return math.inf if winner == str(IA_index + 1) else -math.inf
        if profondeur == 0:
            return self.evaluer(IA_index, poids_avancer=1.2, poids_bloquer=0.8, poids_murs=0.05)
        if self.tour == IA_index:
            best = -math.inf
            for move in self.get_legal_moves():
                score = self.apply_move(move).minMax(profondeur - 1, IA_index)
                best = max(best, score)
            return best
        else:
            best = math.inf
            for move in self.get_legal_moves():
                score = self.apply_move(move).minMax(profondeur - 1, IA_index)
                best = min(best, score)
            return best
    """

    def minimax(self, profondeur: int, IA_index: int, alpha: float = -math.inf, beta: float = math.inf,
                  poids_avancer=1.2, poids_bloquer=0.8, poids_murs=0.1, 
                  poids_avance=0.5) -> float:
        """
        Fonction min max avec élagage alpha béta. Cette fonction retourne la valeur de l'état de jeux du point de vu du joueur.
        La fonction est récursive.
        """
        # On vérifie dans la table de transposition si cet état est déjà connu.
        state_hash = self.get_hash()
        if state_hash in TRANSPOSITION_TABLE:
            stored_depth, stored_value = TRANSPOSITION_TABLE[state_hash]
            if stored_depth >= profondeur:
                return stored_value
        
        # On vérifie que la partie n'est pas finit
        if self.is_terminal():
            winner = self.get_winner()
            return 1000 if winner == str(IA_index + 1) else -1000
        
        # Condition d'arret de cette fonction récursive.
        if profondeur == 0:
            return self.evaluer(IA_index, poids_avancer, poids_bloquer, poids_murs, 
                              poids_avance)
        
        # Noeud MAX, c'est à dire le tour du joueur IA. Dans le mode de jeux 3, c'est le tour de l'IA qui appeller cette fonction.
        if self.tour == IA_index:
            value = -math.inf
            for move in self.get_legal_moves():
                nouvel_etat = self.apply_move(move)
                if nouvel_etat:
                    score = nouvel_etat.minimax(
                        profondeur - 1, IA_index, alpha, beta, 
                        poids_avancer, poids_bloquer, poids_murs,
                        poids_avance
                    )
                    value = max(value, score)
                    alpha = max(alpha, value)
                    if alpha >= beta:
                        break
            
            TRANSPOSITION_TABLE[state_hash] = (profondeur, value)
            return value

        # Noued MIN tour de l'adversaire.
        else:
            value = math.inf
            for move in self.get_legal_moves():
                nouvel_etat = self.apply_move(move)
                if nouvel_etat:
                    score = nouvel_etat.minimax(
                        profondeur - 1, IA_index, alpha, beta, 
                        poids_avancer, poids_bloquer, poids_murs,
                        poids_avance
                    )
                    value = min(value, score)
                    beta = min(beta, value)
                    if beta <= alpha:
                        break
            
            TRANSPOSITION_TABLE[state_hash] = (profondeur, value)
            return value
    
    def choix_coup(self, profondeur=3, IA_index=None, epsilon=0.0,
                  poids_avancer=1.2, poids_bloquer=0.8, poids_murs=0.1,
                  poids_avance=0.5) -> tuple:
        """
        Fonction permettant de choisir un coup parmi tous les coups possibles.
        """
        if IA_index is None:
            IA_index = self.tour
        
        # récupération des coups possibles
        coups_possibles = self.get_legal_moves()
        
        if not coups_possibles:
            print("Aucun coup possible!")
            return None

        # Si un seul coup possible on le joue.
        if len(coups_possibles) == 1:
            return coups_possibles[0]
        
        # si l'action est une action de victoire on le joue.
        for coup in coups_possibles:
            nouvel_etat = self.apply_move(coup)
            if nouvel_etat and nouvel_etat.is_terminal():
                return coup
        
        if random.random() < epsilon:
            return random.choice(coups_possibles)
        
        meilleur_score = float('-inf')
        meilleur_coup = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Recherche du meilleur coup en simulant le coup et en evaluant l'état du jeu après ce coup.
        for coup in coups_possibles:
            nouvel_etat = self.apply_move(coup)
            if nouvel_etat is None:
                continue
                
            score = -nouvel_etat.minimax(
                profondeur-1, 1-IA_index, -beta, -alpha,
                poids_avancer, poids_bloquer, poids_murs,
                poids_avance
            )
            
            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = coup
                
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        # Condition si aucun meilleur coup n'est trouvé.
        if meilleur_coup is None and coups_possibles:
            meilleur_coup = coups_possibles[0]
            
        return meilleur_coup

