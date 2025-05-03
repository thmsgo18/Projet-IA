# GameState.py
import queue
import math
import random
from Object.Plateau import Plateau
from Object.Joueur import Joueur

class GameState:
    def __init__(self, plateau: Plateau, joueurs: list[Joueur], tour: int):
        self.plateau = plateau
        self.joueurs = joueurs
        self.tour = tour

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

    def get_legal_moves(self) -> list:
        moves = []
        joueur = self.joueurs[self.tour]
        x0, y0 = joueur.position
        dim = len(self.plateau.matrice)

        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            x1, y1 = x0 + dx, y0 + dy
            s2 = self.clone()
            if s2.joueurs[s2.tour].deplacer((x1, y1), s2.plateau):
                moves.append(("move", (x1, y1)))

        if joueur.nb_murs > 0:
            for x in range(1, dim, 2):
                for y in range(1, dim, 2):
                    for ori in ("horizontal", "vertical"):
                        s2 = self.clone()
                        if not s2.plateau.placer_mur(x, y, ori):
                            continue
                        if all(s2.plateau.chemin_existe(p.position, p.ligne_obj) for p in s2.joueurs):
                            moves.append(("wall", x, y, ori))
        return moves

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

    def evaluer(self, IA_index: int, poids_avancer=1.0, poids_bloquer=1.0, poids_murs=0.1) -> float:
        moi = self.joueurs[IA_index]
        opp = self.joueurs[1 - IA_index]

        d_moi = self.shortest_path_length(self.plateau, moi.position, moi.ligne_obj)
        d_opp = self.shortest_path_length(self.plateau, opp.position, opp.ligne_obj)

        score_avancer = -poids_avancer * d_moi
        score_bloquer = poids_bloquer * d_opp
        score_murs = poids_murs * (moi.nb_murs - opp.nb_murs)

        return score_avancer + score_bloquer + score_murs

    def shortest_path_length(self, plateau: Plateau, start: tuple, target_line: int) -> float:
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

    def alpha_beta(self, profondeur: int, IA_index: int,
                   alpha: float = -math.inf,
                   beta: float = math.inf) -> float:
        # Cas terminal
        if self.is_terminal():
            winner = self.get_winner()
            return math.inf if winner == str(IA_index + 1) else -math.inf
        # Cas profondeur zéro
        if profondeur == 0:
            return self.evaluer(IA_index)
        # Max node
        if self.tour == IA_index:
            value = -math.inf
            for move in self.get_legal_moves():
                score = self.apply_move(move).alpha_beta(profondeur - 1, IA_index, alpha, beta)
                value = max(value, score)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # coupure beta
            return value
        # Min node
        else:
            value = math.inf
            for move in self.get_legal_moves():
                score = self.apply_move(move).alpha_beta(profondeur - 1, IA_index, alpha, beta)
                value = min(value, score)
                beta = min(beta, value)
                if beta <= alpha:
                    break  # coupure alpha
            return value

    def choix_coup(self, profondeur: int, IA_index: int,
                   epsilon: float = 0.3, temperature: float = 0.5) -> tuple:
        legal = self.get_legal_moves()
        # 1) Si un coup permet de gagner immédiatement, on le joue
        for move in legal:
            if self.apply_move(move).is_terminal():
                return move
        random.shuffle(legal)  # Ajoute de la variation naturelle

        # Epsilon-greedy : exploration aléatoire
        if random.random() < epsilon:
            return random.choice(legal)

        # Sinon softmax basée sur alpha-bêta
        scores = [self.apply_move(m).alpha_beta(profondeur - 1, IA_index) for m in legal]
        exps = [math.exp(s / temperature) for s in scores]
        return random.choices(legal, weights=exps, k=1)[0]
