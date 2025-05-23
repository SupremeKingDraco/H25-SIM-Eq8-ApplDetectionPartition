from music21 import converter, interval, pitch, note, chord
from copy import deepcopy

def transposer_midi(chemin,hauteur_cible_utilisateur):
    """
    Fonction principale pour charger un fichier MIDI, le transposer dans une tonalité définie par l'utilisateur,
    et sauvegarder la version transposée.
    """

    # Définir le chemin vers votre fichier MIDI
    chemin_midi = chemin

    # Nouvelle Gamme
    hauteur_cible = pitch.Pitch( hauteur_cible_utilisateur)

    # Charger le fichier MIDI original
    try:
        flux_original = converter.parse(chemin_midi)
    except Exception as e:
        print(f"  Erreur lors du chargement du fichier MIDI : {e}")
        return

    # Faire une copie profonde du flux avant de le modifier
    flux_transpose = deepcopy(flux_original)

    # Essayer d'analyser la tonalité originale de la pièce
    try:
        tonalite_originale = flux_original.analyze('key')
        print(f"\nTonalité originale : {tonalite_originale.tonic.name} {tonalite_originale.mode}")
        hauteur_tonique_originale = tonalite_originale.tonic
    except Exception as e:
        print(f"\n   Impossible de détecter la tonalité : {e}")
        hauteur_tonique_originale = pitch.Pitch("C")
        print("Supposons que la tonalité originale est C Majeur.")

    # Calculer l'intervalle entre la tonique originale et la hauteur cible
    try:
        intervalle_transposition = interval.Interval(hauteur_tonique_originale, hauteur_cible)
    except Exception as e:
        print(f"  Erreur lors du calcul de l'intervalle : {e}")
        return

    # Appliquer la transposition au flux copié
    try:
        flux_transpose = flux_transpose.transpose(intervalle_transposition)
    except Exception as e:
        print(f"  Échec de la transposition : {e}")
        return

    # Sauvegarder le flux transposé en tant que nouveau fichier MIDI
    try:
        midi_sortie = f"transpose_vers_nouvelle_tonalite.mid"
        flux_transpose.write('midi', fp=midi_sortie)
        print(f"\n MIDI transposé sauvegardé sous le nom '{midi_sortie}'")
    except Exception as e:
        print(f"  Erreur lors de la sauvegarde du fichier : {e}")


