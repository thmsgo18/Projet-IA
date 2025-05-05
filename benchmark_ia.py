#!/usr/bin/env python3
# benchmark_ia.py
# Script pour lancer 50 parties IA contre IA avec différentes combinaisons de difficultés

import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from Object.Plateau import Plateau
from Object.Joueur import Joueur
from GameState import GameState, TRANSPOSITION_TABLE

# Paramètres pour les différents niveaux d'IA
IA_LEVELS = {
    "facile": {
        "profondeur": 1,
        "epsilon": 0.4,
        "poids_avancer": 1,
        "poids_bloquer": 0.5,
        "poids_murs": 0.2,
        "poids_avance": 0.3
    },
    "moyen": {
        "profondeur": 2,
        "epsilon": 0.2,
        "poids_avancer": 1.2,
        "poids_bloquer": 0.8,
        "poids_murs": 0.3,
        "poids_avance": 0.5
    },
    "difficile": {
        "profondeur": 3,
        "epsilon": 0.1,
        "poids_avancer": 1.5,
        "poids_bloquer": 1,
        "poids_murs": 0.4,
        "poids_avance": 0.7
    }
}

# Combinaisons de difficultés à tester
COMBINATIONS = [
    ("facile", "facile"),
    ("facile", "moyen"),
    ("facile", "difficile"),
    ("moyen", "moyen"),
    ("moyen", "difficile"),
    ("difficile", "difficile")
]

# Nombre de parties par combinaison
NB_PARTIES = 50

def initialiser_jeu():
    """Initialise un nouveau jeu de Quoridor"""
    plateau = Plateau()
    max_idx = 2 * plateau.taille - 2  # 16 si taille=9
    mid = plateau.taille - 1  # 8
    
    # Instanciation des joueurs
    joueurs = [
        Joueur("1", (0, mid), max_idx),
        Joueur("2", (max_idx, mid), 0)
    ]
    
    for j in joueurs:
        plateau.placer_joueur(j)
    
    return GameState(plateau, joueurs, 0)

def jouer_partie(niveau_ia1, niveau_ia2, max_coups=200):
    """
    Joue une partie complète entre deux IAs de niveaux spécifiés
    
    Args:
        niveau_ia1: niveau de l'IA 1 ("facile", "moyen", "difficile")
        niveau_ia2: niveau de l'IA 2 ("facile", "moyen", "difficile")
        max_coups: nombre maximum de coups avant match nul
    
    Returns:
        gagnant: "1", "2" ou None (match nul)
        nb_coups: nombre de coups joués
    """
    # Vider la table de transposition pour chaque nouvelle partie
    TRANSPOSITION_TABLE.clear()
    
    # Initialiser le jeu
    state = initialiser_jeu()
    
    # Paramètres des IAs
    params_ia = [IA_LEVELS[niveau_ia1], IA_LEVELS[niveau_ia2]]
    
    nb_coups = 0
    
    # Boucle de jeu
    while nb_coups < max_coups:
        # Vérifier victoire
        for j in state.joueurs:
            if j.position[0] == j.ligne_obj:
                return j.nom, nb_coups
        
        # Tour actuel
        tour = state.tour
        
        # Paramètres de l'IA courante
        params = params_ia[tour]
        
        # Choisir le meilleur coup
        best_move = state.choix_coup(
            profondeur=params["profondeur"],
            IA_index=tour,
            epsilon=params["epsilon"],
            poids_avancer=params["poids_avancer"],
            poids_bloquer=params["poids_bloquer"],
            poids_murs=params["poids_murs"],
            poids_avance=params["poids_avance"]
        )
        
        # Si aucun coup n'est possible, c'est un match nul
        if best_move is None:
            print(f"  Aucun coup possible pour le joueur {tour+1}")
            return None, nb_coups
        
        # Appliquer le coup
        state = state.apply_move(best_move)
        nb_coups += 1
    
    # Si on arrive ici, c'est un match nul
    return None, nb_coups

def lancer_benchmark():
    """Lance le benchmark et affiche les résultats"""
    print("Lancement du benchmark IA contre IA...")
    print(f"Nombre de parties par combinaison: {NB_PARTIES}")
    
    # Dictionnaire pour stocker les résultats
    resultats = {}
    
    # Pour chaque combinaison de difficultés
    for niveau_ia1, niveau_ia2 in COMBINATIONS:
        print(f"\nTest: {niveau_ia1.capitalize()} vs {niveau_ia2.capitalize()}")
        
        # Initialiser les compteurs
        victoires_ia1 = 0
        victoires_ia2 = 0
        matchs_nuls = 0
        total_coups = 0
        
        debut = time.time()
        
        # Jouer les parties
        for i in range(NB_PARTIES):
            if (i + 1) % 10 == 0:
                print(f"  Partie {i + 1}/{NB_PARTIES}...")
            
            gagnant, nb_coups = jouer_partie(niveau_ia1, niveau_ia2)
            
            if gagnant == "1":
                victoires_ia1 += 1
            elif gagnant == "2":
                victoires_ia2 += 1
            else:
                matchs_nuls += 1
            
            total_coups += nb_coups
        
        duree = time.time() - debut
        
        # Stocker les résultats
        resultats[(niveau_ia1, niveau_ia2)] = {
            "victoires_ia1": victoires_ia1,
            "victoires_ia2": victoires_ia2,
            "matchs_nuls": matchs_nuls,
            "coups_moyen": total_coups / NB_PARTIES,
            "duree": duree
        }
        
        # Afficher les résultats de cette combinaison
        print(f"  Résultats: {niveau_ia1.capitalize()} a gagné {victoires_ia1} fois, "
              f"{niveau_ia2.capitalize()} a gagné {victoires_ia2} fois, "
              f"{matchs_nuls} matchs nuls")
        print(f"  Nombre moyen de coups: {total_coups / NB_PARTIES:.1f}")
        print(f"  Durée: {duree:.1f} secondes")
    
    return resultats

def afficher_resultats(resultats):
    """Affiche les résultats sous forme de tableau et de graphiques"""
    # Créer un DataFrame pour les résultats
    data = []
    for (niveau_ia1, niveau_ia2), res in resultats.items():
        data.append({
            "IA1": niveau_ia1.capitalize(),
            "IA2": niveau_ia2.capitalize(),
            "Victoires IA1": res["victoires_ia1"],
            "Victoires IA2": res["victoires_ia2"],
            "Matchs nuls": res["matchs_nuls"],
            "Coups moyen": res["coups_moyen"],
            "Durée (s)": res["duree"]
        })
    
    df = pd.DataFrame(data)
    
    # Afficher le tableau
    print("\nRésultats complets:")
    print(df.to_string(index=False))
    
    # Créer une matrice pour le heatmap des victoires
    niveaux = ["Facile", "Moyen", "Difficile"]
    victoires_ia1 = np.zeros((3, 3))
    victoires_ia2 = np.zeros((3, 3))
    
    for i, n1 in enumerate(["facile", "moyen", "difficile"]):
        for j, n2 in enumerate(["facile", "moyen", "difficile"]):
            if (n1, n2) in resultats:
                res = resultats[(n1, n2)]
                victoires_ia1[i, j] = res["victoires_ia1"]
                victoires_ia2[i, j] = res["victoires_ia2"]
    
    # Créer les visualisations
    plt.figure(figsize=(15, 10))
    
    # Heatmap des victoires de l'IA1
    plt.subplot(2, 2, 1)
    sns.heatmap(victoires_ia1, annot=True, fmt='g', cmap='Blues',
                xticklabels=niveaux, yticklabels=niveaux)
    plt.title("Victoires de l'IA1")
    plt.xlabel("Niveau IA2")
    plt.ylabel("Niveau IA1")
    
    # Heatmap des victoires de l'IA2
    plt.subplot(2, 2, 2)
    sns.heatmap(victoires_ia2, annot=True, fmt='g', cmap='Reds',
                xticklabels=niveaux, yticklabels=niveaux)
    plt.title("Victoires de l'IA2")
    plt.xlabel("Niveau IA2")
    plt.ylabel("Niveau IA1")
    
    # Graphique en barres des victoires par combinaison
    plt.subplot(2, 1, 2)
    
    # Préparer les données pour le graphique en barres
    labels = [f"{row['IA1']} vs {row['IA2']}" for _, row in df.iterrows()]
    victoires_ia1_data = [row['Victoires IA1'] for _, row in df.iterrows()]
    victoires_ia2_data = [row['Victoires IA2'] for _, row in df.iterrows()]
    matchs_nuls_data = [row['Matchs nuls'] for _, row in df.iterrows()]
    
    x = np.arange(len(labels))
    width = 0.25
    
    plt.bar(x - width, victoires_ia1_data, width, label='Victoires IA1', color='blue')
    plt.bar(x, victoires_ia2_data, width, label='Victoires IA2', color='red')
    plt.bar(x + width, matchs_nuls_data, width, label='Matchs nuls', color='gray')
    
    plt.xlabel('Combinaisons')
    plt.ylabel('Nombre de parties')
    plt.title('Résultats des parties par combinaison de difficultés')
    plt.xticks(x, labels, rotation=45)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('resultats_benchmark.png')
    plt.show()

if __name__ == "__main__":
    resultats = lancer_benchmark()
    afficher_resultats(resultats)
