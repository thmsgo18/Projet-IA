# GameState.py
import queue
import math
import random
import hashlib
from Object.Plateau import Plateau
from Object.Joueur import Joueur

# Table de transposition globale
TRANSPOSITION_TABLE = {}

class GameState:
    def __init__(self, plateau: Plateau, joueurs: list[Joueur], tour: int):
        self.plateau = plateau
        self.joueurs = joueurs
        self.tour = tour
        self._hash = None  # Cache pour le hash de l'état

    def get_hash(self) -> str:
        """Génère un hash unique pour l'état actuel du jeu"""
        if self._hash is not None:
            return self._hash
            
        # Représentation de l'état sous forme de chaîne
        state_str = ""
        # Ajouter l'état du plateau
        for row in self.plateau.matrice:
            state_str += ''.join(str(cell) for cell in row)
        # Ajouter les positions et murs des joueurs
        for j in self.joueurs:
            state_str += f"{j.position[0]},{j.position[1]},{j.nb_murs}"
        # Ajouter le tour actuel
        state_str += str(self.tour)
        
        # Générer le hash
        self._hash = hashlib.md5(state_str.encode()).hexdigest()
        return self._hash

    def clone(self) -> "GameState":
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
        """Retourne la liste des déplacements légaux pour le joueur actuel.
        
        Paramètres:
            joueur: le joueur qui se déplace
            x0, y0: position actuelle du joueur
            dim: dimension du plateau
            
        Retourne:
            moves: liste des déplacements possibles
        """
        moves = []
        # Liste des deplacements possibles : haut, bas, gauche, droite
        directions = [(-2,0), (2,0), (0,-2), (0,2)]
        
        # Vérification des deplacements
        for dx, dy in directions:
            x1, y1 = x0 + dx, y0 + dy
            
            # Vérification des limites du plateau
            if not (0 <= x1 < dim and 0 <= y1 < dim):
                continue
            
            # Vérification des murs bloquant
            mx, my = (x0 + x1)//2, (y0 + y1)//2
            if self.plateau.matrice[mx][my] == Plateau.WALL:
                continue
            
            # Vérification des cases occupées
            occupied = False
            for p in self.joueurs:
                if p.position == (x1, y1):
                    occupied = True
                    break
                    
            if occupied:
                # Règle spéciale: saut par-dessus un joueur
                moves.extend(self._verifier_saut(x1, y1, dx, dy, dim))
            else:
                # Déplacement normal
                moves.append(("move", (x1, y1)))
                
        return moves
    
    def _verifier_saut(self, x1, y1, dx, dy, dim) -> list:
        """Vérifie si un saut par-dessus un joueur est possible.
        
        Paramètres:
            x1, y1: position du joueur par-dessus lequel on saute
            dx, dy: direction du saut
            dim: dimension du plateau
            
        Retourne:
            moves: liste des sauts possibles
        """
        moves = []
        # Position après le saut
        x2, y2 = x1 + dx, y1 + dy
        
        # Vérification des limites du plateau
        if 0 <= x2 < dim and 0 <= y2 < dim:
            # Vérification des murs bloquant
            mx2, my2 = (x1 + x2)//2, (y1 + y2)//2
            if self.plateau.matrice[mx2][my2] != Plateau.WALL:
                # Vérification des cases occupées
                if not any(p.position == (x2, y2) for p in self.joueurs):
                    moves.append(("move", (x2, y2)))
        return moves
    
    def _get_wall_positions(self, adversaire, dim) -> list:
        """Génère les positions stratégiques pour placer des murs.
        
        Paramètres:
            adversaire: le joueur adversaire
            dim: dimension du plateau
            
        Retourne:
            wall_positions: liste des positions possibles pour les murs
        """
        # Positions près de l'adversaire (pour le bloquer)
        wall_positions = []
        px, py = adversaire.position
        
        # Positions devant l'adversaire (pour le bloquer dans sa progression)
        direction = -1 if adversaire.ligne_obj == 0 else 1
        front_x = px + direction * 2  # Position devant l'adversaire
        
        # Ajouter des positions stratégiques devant l'adversaire
        if 1 <= front_x < dim-1:
            for offset in [-2, 0, 2]:
                wx, wy = front_x, py + offset
                if 1 <= wy < dim-1 and wx % 2 == 1 and wy % 2 == 1:
                    wall_positions.append((wx, wy))
        
        # Ajouter des positions autour de l'adversaire
        for i in range(-3, 4, 2):
            for j in range(-3, 4, 2):
                wx, wy = px + i, py + j
                if 1 <= wx < dim-1 and 1 <= wy < dim-1 and wx % 2 == 1 and wy % 2 == 1:
                    wall_positions.append((wx, wy))
        
        # Limiter le nombre de positions pour améliorer les performances
        max_walls = 18  # Valeur fixe, sans notion de phase
        if len(wall_positions) > max_walls:
            wall_positions = wall_positions[:max_walls]
        
        return wall_positions
    
    def _verifier_placement_mur(self, x, y, orientation, adversaire, d_adversaire) -> tuple:
        """Vérifie si un mur peut être placé et s'il est efficace.
        
        Paramètres:
            x, y: position du mur
            orientation: orientation du mur ("h" ou "v")
            adversaire: le joueur adversaire
            d_adversaire: distance actuelle de l'adversaire à son objectif
            
        Retourne:
            (valide, coup): si le mur est valide et le coup correspondant
        """
        # Vérifier si un mur est déjà présent
        if orientation == "h":
            if (self.plateau.matrice[x][y-1] == Plateau.WALL or 
                self.plateau.matrice[x][y+1] == Plateau.WALL):
                return (False, None)
        else:  # vertical (v)
            if (self.plateau.matrice[x-1][y] == Plateau.WALL or 
                self.plateau.matrice[x+1][y] == Plateau.WALL):
                return (False, None)
        
        # Cloner et vérifier si le mur peut être placé
        s2 = self.clone()
        if not s2.plateau.placer_mur(x, y, orientation):
            return (False, None)
        
        # Vérifier que tous les joueurs ont un chemin vers leur objectif
        if all(s2.plateau.chemin_existe(p.position, p.ligne_obj) for p in s2.joueurs):
            # Vérifier si ce mur augmente la distance de l'adversaire
            new_d_adv = s2.bfs(s2.plateau, adversaire.position, adversaire.ligne_obj)
            
            # Ajouter le mur s'il est efficace (augmente la distance de l'adversaire d'au moins 1)
            if new_d_adv > d_adversaire:
                return (True, ("wall", x, y, orientation))
            
            # Parfois accepter des murs même s'ils n'augmentent pas la distance
            # Cela permet plus de diversité dans le jeu
            elif new_d_adv == d_adversaire and random.random() < 0.3:
                return (True, ("wall", x, y, orientation))
                
        return (False, None)
    
    def get_legal_moves(self) -> list:
        """Retourne la liste des coups légaux pour le joueur actuel.
        
        Retourne:
            moves: liste de tuples représentant les coups possibles
                  format: ("move", (x, y)) ou ("wall", x, y, orientation)
        """
        joueur = self.joueurs[self.tour]
        x0, y0 = joueur.position
        dim = len(self.plateau.matrice)
        adversaire = self.joueurs[1 - self.tour]
        
        # 1. Générer les déplacements possibles
        moves = self._get_legal_moves_deplacement(joueur, x0, y0, dim)
        
        # 2. Générer les placements de murs possibles
        if joueur.nb_murs > 0:
            # Calculer les distances actuelles vers les objectifs
            d_moi = self.bfs(self.plateau, joueur.position, joueur.ligne_obj)
            d_adversaire = self.bfs(self.plateau, adversaire.position, adversaire.ligne_obj)
            
            # Générer les positions stratégiques pour les murs
            wall_positions = self._get_wall_positions(adversaire, dim)
            
            # Essayer de placer des murs aux positions sélectionnées
            for x, y in wall_positions:
                for orientation in ["h", "v"]:
                    valide, coup = self._verifier_placement_mur(x, y, orientation, adversaire, d_adversaire)
                    if valide:
                        moves.append(coup)
        
        # Trier les coups: déplacements d'abord, puis murs
        move_moves = [m for m in moves if m[0] == "move"]
        wall_moves = [m for m in moves if m[0] == "wall"]
        
        return move_moves + wall_moves
    
    def calculer_chemin(self, plateau: Plateau, depart: tuple, arrivee: int) -> list:
        """Calcule le chemin le plus court et le retourne comme une liste de positions"""
        visited = {depart}
        q = queue.Queue()
        q.put((depart, [depart]))  # (position, chemin)
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
        return []  # Aucun chemin trouvé

    def apply_move(self, move: tuple) -> "GameState":
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
        """Fonction d'évaluation simplifiée pour l'algorithme minimax.
        
        Paramètres:
            IA_index: indice du joueur IA (0 ou 1)
            poids_avancer: importance de se rapprocher de son objectif
            poids_bloquer: importance de bloquer l'adversaire
            poids_murs: importance des murs restants
            poids_avance: importance de l'avance dans la course
        
        Retourne:
            score: valeur d'évaluation de l'état (plus élevé = meilleur pour l'IA)
        """
        # Récupérer les joueurs
        moi = self.joueurs[IA_index]
        adversaire = self.joueurs[1 - IA_index]
        
        # Calculer les distances via le plus court chemin
        d_moi = self.bfs(self.plateau, moi.position, moi.ligne_obj)
        d_adversaire = self.bfs(self.plateau, adversaire.position, adversaire.ligne_obj)
        
        # 1. Score pour se rapprocher de son objectif (négatif car on veut minimiser la distance)
        score_avancer = -poids_avancer * d_moi
        
        # 2. Score pour bloquer l'adversaire (positif car on veut maximiser sa distance)
        score_bloquer = poids_bloquer * d_adversaire
        
        # 3. Score pour les murs restants
        # Ajustement: les murs sont plus importants en fin de partie
        importance_murs = poids_murs
        if d_moi <= 4 or d_adversaire <= 4:  # Fin de partie
            importance_murs = poids_murs * 2
        score_murs = importance_murs * (moi.nb_murs - adversaire.nb_murs)
        
        # 4. Bonus pour être en avance dans la course
        avantage_relatif = d_adversaire - d_moi
        bonus_avance = poids_avance * avantage_relatif
        
        # Combiner tous les scores
        return score_avancer + score_bloquer + score_murs + bonus_avance

    def bfs(self, plateau: Plateau, start: tuple, target_line: int) -> float:
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
        joueur_actuel = self.joueurs[self.tour]
        return joueur_actuel.position[0] == joueur_actuel.ligne_obj

    def get_winner(self) -> str:
        for j in self.joueurs:
            if j.position[0] == j.ligne_obj:
                return j.nom
        return None
    """
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
        """Algorithme minimax avec élagage alpha-beta et paramètres personnalisables
        
        Args:
            profondeur: profondeur de recherche restante
            IA_index: indice du joueur IA (0 ou 1)
            alpha: valeur alpha pour l'élagage
            beta: valeur beta pour l'élagage
            poids_avancer: importance de se rapprocher de son objectif
            poids_bloquer: importance de bloquer l'adversaire
            poids_murs: importance des murs restants
            poids_avance: importance de l'avance dans la course
            
        Returns:
            score: valeur d'évaluation de l'état
        """
        # Vérifier si l'état est dans la table de transposition
        state_hash = self.get_hash()
        if state_hash in TRANSPOSITION_TABLE:
            stored_depth, stored_value = TRANSPOSITION_TABLE[state_hash]
            if stored_depth >= profondeur:
                return stored_value
        
        # Cas terminal
        if self.is_terminal():
            winner = self.get_winner()
            return 1000 if winner == str(IA_index + 1) else -1000
            
        # Cas profondeur zéro
        if profondeur == 0:
            return self.evaluer(IA_index, poids_avancer, poids_bloquer, poids_murs, 
                              poids_avance)
            
        # Max node (tour du joueur IA)
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
                        break  # Élagage beta
            
            # Stocker le résultat dans la table de transposition
            TRANSPOSITION_TABLE[state_hash] = (profondeur, value)
            return value
            
        # Min node (tour de l'adversaire)
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
                        break  # Élagage alpha
            
            # Stocker le résultat dans la table de transposition
            TRANSPOSITION_TABLE[state_hash] = (profondeur, value)
            return value
    
    def choix_coup(self, profondeur=3, IA_index=None, epsilon=0.0,
                  poids_avancer=1.2, poids_bloquer=0.8, poids_murs=0.1,
                  poids_avance=0.5) -> tuple:
        """Choix du meilleur coup à jouer avec minimax + élagage alpha-beta
        
        Args:
            profondeur: profondeur de recherche
            IA_index: indice du joueur IA (0 ou 1)
            epsilon: probabilité de choisir un coup aléatoire (exploration)
            poids_avancer: importance de se rapprocher de son objectif
            poids_bloquer: importance de bloquer l'adversaire
            poids_murs: importance des murs restants
            poids_avance: importance de l'avance dans la course
        Returns:
            meilleur_coup: le coup choisi
        """
        
        if IA_index is None:
            IA_index = self.tour
            
        # Générer les coups possibles
        coups_possibles = self.get_legal_moves()
        
        # Vérifier s'il y a des coups possibles
        if not coups_possibles:
            # Aucun coup possible, situation rare mais possible
            print("Aucun coup possible!")
            return None
        
        # Si un seul coup possible, le jouer directement
        if len(coups_possibles) == 1:
            return coups_possibles[0]
        
        # Vérifier si on peut gagner immédiatement
        for coup in coups_possibles:
            nouvel_etat = self.apply_move(coup)
            if nouvel_etat and nouvel_etat.is_terminal():
                return coup
        
        # Exploration: choisir un coup aléatoire avec probabilité epsilon
        if random.random() < epsilon:
            return random.choice(coups_possibles)
        
        # Exploitation: recherche minimax avec élagage alpha-beta
        meilleur_score = float('-inf')
        meilleur_coup = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Évaluer chaque coup possible
        for coup in coups_possibles:
            # Simuler le coup
            nouvel_etat = self.apply_move(coup)
            if nouvel_etat is None:
                continue  # Coup invalide
                
            # Évaluer récursivement avec minimax
            score = -nouvel_etat.minimax(
                profondeur-1, 1-IA_index, -beta, -alpha,
                poids_avancer, poids_bloquer, poids_murs,
                poids_avance
            )
            
            # Mettre à jour le meilleur coup
            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = coup
                
            # Mise à jour d'alpha pour l'élagage
            alpha = max(alpha, score)
            if alpha >= beta:
                break  # Élagage beta
        
        # Si aucun coup valide trouvé, prendre le premier
        if meilleur_coup is None and coups_possibles:
            meilleur_coup = coups_possibles[0]
            
        # Retourner le meilleur coup trouvé
        return meilleur_coup

