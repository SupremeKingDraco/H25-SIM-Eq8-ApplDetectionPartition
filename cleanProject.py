import cv2
import numpy as np
from music21 import *


def process_video_and_generate_midi(nom_chanson: str, vrai_bpm_chanson: int, nombre_armure: int, commencement: int, gamme: int,  pixels_selectionnes=[(52, 297), (69, 340), (99, 341), (133, 294), (149, 344), (179, 346), (207, 340), (247, 299), (265, 336), (290, 335), (330, 294), (351, 337), (372, 338), (409, 338), (443, 281), (454, 336), (489, 342), (525, 297), (540, 339), (570, 339), (598, 340)]):
    """
    This function processes a video to detect pixel changes and generates a MIDI file.

    Parameters:
        nom_chanson (str): Path to the input video file.
        notes (list): List of musical notes corresponding to the detected pixels.
        gamme (int): Starting octave for the notes.
        vrai_bpm_chanson (int): Actual BPM of the song.
        pixels_selectionnes (list): List of pixel coordinates to monitor for changes.
        tolerence (int): Tolerance threshold for detecting significant color changes.
        commencement (int): Index to start assigning notes from the `notes` list.
        valeur_de_multiplication (int): Multiplier for BPM conversion.
    """

    # Set up detection
    valeur_de_multiplication = 16
    tolerence = 100
    array_pixel = []
    frame_correction = -1
    bpm_chanson = vrai_bpm_chanson * valeur_de_multiplication
    bpm_chanson = bpm_chanson / 60
    notes = ["C", "D", "E", "F", "G", "A", "B"]

    ordre_des_dieses = ["F#", "C#", "G#", "D#", "A#", "E#", "B#"]
    ordre_des_bemols = ["F-", "C-", "G-", "D-", "A-", "E-", "B-"]

    if nombre_armure > 0:
        a_modifier = ordre_des_dieses[:nombre_armure]
        for acc in a_modifier:
            note_base = acc[0]
            index = notes.index(note_base)
            notes[index] = acc
    elif nombre_armure < 0:
        nombre_armure = abs(nombre_armure)
        a_modifier = ordre_des_bemols[:nombre_armure]
        for acc in a_modifier:
            note_base = acc[0]
            index = notes.index(note_base)
            notes[index] = acc

    print("Notes modifiées :", notes)


    class Pixel:
        def __init__(self, coordonnee, valeur_initiale):
            self.coordonnee = coordonnee
            self.valeur_initiale = valeur_initiale
            self.note = None
            self.frames_changement = []

    # Fonction de rappel de la souris pour capturer les pixels sélectionnés
    def selectionner_pixel(event, x, y, flags, param):
        nonlocal pixels_selectionnes, frame
        if event == cv2.EVENT_LBUTTONDOWN:
            pixels_selectionnes.append((x, y))
            array_pixel.append(Pixel((x, y), frame[y, x]))
            print(f"Pixel sélectionné : ({x}, {y}) avec valeur initiale : {frame[y, x]}")
            # Dessiner un cercle au pixel sélectionné
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            cv2.imshow('Sélectionner Pixels', frame)

    def selectionner_pixel_auto():
        nonlocal pixels_selectionnes, frame
        for pixelAuto in pixels_selectionnes:
            x, y = pixelAuto
            array_pixel.append(Pixel((x, y), frame[y, x]))
            print(f"Pixel sélectionné : ({x}, {y}) avec valeur initiale : {frame[y, x]}")

    def changerY():
        nonlocal pixels_selectionnes
        for i in range(len(pixels_selectionnes)):
            x, y = pixels_selectionnes[i]
            y = 1
            pixels_selectionnes[i] = (x, y)

    def pixel_to_note():
        nonlocal array_pixel, gamme
        compteur = commencement
        for pixel in array_pixel:
            nomNote = notes[compteur]
            pixel.note = nomNote + str(gamme)
            compteur += 1
            if compteur > 6:
                compteur = 0
                gamme += 1

    def calculer_diff(valeurPrecedente, valeurActuelle, compteurFrame):
        r1, g1, b1 = valeurPrecedente
        r2, g2, b2 = valeurActuelle
        if (max(r1, r2) - min(r1, r2) > tolerence or max(g1, g2) - min(g1, g2) > tolerence or max(b1, b2) - min(b1,
                                                                                                                b2) > tolerence) and compteurFrame > frame_cible and compteurFrame < 7479:
            return True
        return False

    def trouver_valeur_proche(valeurEntree):
        # Définir les multiples
        multiple0_25 = 0.25
        multiple1_3 = 1 / 3

        # Vérifier si la valeur est proche de zéro
        if abs(valeurEntree) < 0.01:
            return 0.0

        # Calculer les multiples les plus proches
        multipleProche0_125 = round(valeurEntree / multiple0_25) * multiple0_25
        multipleProche1_3 = round(valeurEntree / multiple1_3) * multiple1_3

        # Déterminer quel multiple est le plus proche
        if abs(valeurEntree - multipleProche0_125) < abs(valeurEntree - multipleProche1_3):
            valeurProche = multipleProche0_125
        else:
            valeurProche = multipleProche1_3

        # Arrondir le résultat à trois décimales
        return round(valeurProche, 3)

    # Charger la vidéo
    cap = cv2.VideoCapture(nom_chanson)

    # Vérifier si la vidéo s'est ouverte correctement
    if not cap.isOpened():
        print("Erreur : Impossible d'ouvrir la vidéo.")
        return

    taux_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Taux de rafraîchissement de la vidéo : {taux_fps} FPS")

    # Lire les frames jusqu'à la frame cible
    compteur_frame = 0
    frame_cible = 140
    frame = None

    while compteur_frame < frame_cible:
        ret, frame = cap.read()
        if not ret:
            print("Erreur : Impossible de lire la frame.")
            return
        compteur_frame += 1

    if len(pixels_selectionnes) > 0:
        selectionner_pixel_auto()

    # Afficher la frame cible et permettre à l'utilisateur de sélectionner des pixels
    cv2.imshow('Sélectionner Pixels', frame)
    cv2.setMouseCallback('Sélectionner Pixels', selectionner_pixel)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Vérifier si des pixels ont été sélectionnés
    if not pixels_selectionnes:
        print("Aucun pixel sélectionné. Sortie.")
        return

    # Dictionnaire pour stocker les valeurs RVB précédentes des pixels sélectionnés
    valeurs_precedentes = {pixel: pixel.valeur_initiale for pixel in array_pixel}

    pixel_to_note()

    # Afficher chaque pixel et la note qui lui est attachée
    for pixel in array_pixel:
        print(pixel.valeur_initiale)

    compteur_frame = 0

    # Réinitialiser la capture vidéo au début
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    note_apuuyer_list = []
    fluxMusical = stream.Score()
    partieMusicale = stream.Part()

    fluxMusical.insert(0, tempo.MetronomeMark(vrai_bpm_chanson))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Traiter chaque pixel sélectionné
        for pixel in array_pixel:
            x, y = pixel.coordonnee
            valeur_actuelle = frame[y, x]
            valeur_precedente = valeurs_precedentes[pixel]

            changementtt = calculer_diff(pixel.valeur_initiale, valeur_actuelle, compteur_frame)

            if len(pixel.frames_changement) % 2 == 0:
                if changementtt:
                    if frame_correction == -1:
                        frame_correction = compteur_frame
                    pixel.frames_changement.append(compteur_frame)
                    print(
                        f"Changement significatif détecté à la frame {compteur_frame} pour le pixel {pixel.note} : Diff RVB = {np.sum(np.abs(valeur_actuelle - valeur_precedente))}")

            else:
                if not changementtt:
                    if frame_correction == -1:
                        frame_correction = compteur_frame
                    pixel.frames_changement.append(compteur_frame)
                    print(
                        f"Changement significatif détecté à la frame {compteur_frame} pour le pixel {pixel.note} : Diff RVB = {np.sum(np.abs(valeur_actuelle - valeur_precedente))}")

            # Mettre à jour la valeur précédente
            valeurs_precedentes[pixel] = valeur_actuelle

        # Afficher la frame
        cv2.imshow('Frame', frame)

        # Interrompre la boucle si 'q' est pressé
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        compteur_frame += 1
        print(f"Frame traitée {compteur_frame}")

    # Libérer l'objet de capture vidéo
    cv2.destroyAllWindows()

    # Afficher les numéros de frame où chaque pixel a changé
    print("\nFrames où chaque pixel a changé :")
    for pixel in array_pixel:
        print(f"Pixel {pixel.note} a changé dans les frames : {pixel.frames_changement}")

    frame_correctionSpecialiser = frame_correction

    for pixel in array_pixel:
        note_apuuyer_list.clear()
        compteur = 0
        changement = pixel.frames_changement
        print(pixel.note)
        for change in changement:
            if len(note_apuuyer_list) == 0:
                note_apuuyer_list.append(change)
            elif len(note_apuuyer_list) == 1:
                note_apuuyer_list.append(change)
                note_en_secondes = (note_apuuyer_list[1] - note_apuuyer_list[0]) / taux_fps
                battement = note_en_secondes * bpm_chanson
                valeurProche = trouver_valeur_proche(battement)
                instanceNote = note.Note(pixel.note)
                instanceNote.quarterLength = valeurProche / valeur_de_multiplication
                decalage_en_secondes = (note_apuuyer_list[0] - frame_correction) / taux_fps
                decalage_battement_en_secondes = decalage_en_secondes * bpm_chanson
                valeur_proche_decalage_en_secondes = trouver_valeur_proche(decalage_battement_en_secondes)
                fluxMusical.coreInsert(valeur_proche_decalage_en_secondes / valeur_de_multiplication, instanceNote)
                note_apuuyer_list.clear()

            compteur += 1

    # Libérer à nouveau l'objet de capture vidéo
    cap.release()
    cv2.destroyAllWindows()

    print("Pixel sélectionné")
    print(pixels_selectionnes)

    fluxMusical.write('midi', fp='score20202.mid')
