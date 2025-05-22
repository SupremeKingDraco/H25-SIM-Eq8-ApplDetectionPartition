import cv2
import numpy as np
# from music21 import *


def process_video_and_generate_midi(nomChanson: str, vraiBpmChanson: int, nombreArmure: int, commencement: int, gamme: int,  pixelsSelectionnes=[(10, 291), (36, 251), (51, 293), (65, 293), (92, 242), (114, 243), (124, 292), (139, 289), (168, 247), (179, 293), (198, 292), (222, 247), (244, 252), (256, 297), (274, 289), (299, 254), (311, 294), (329, 291), (357, 257), (376, 253), (384, 291), (403, 286), (432, 248), (442, 289), (462, 290), (488, 257), (508, 259), (518, 291), (538, 292), (562, 254), (574, 288), (592, 292), (617, 254)]):
    """
    This function processes a video to detect pixel changes and generates a MIDI file.

    Parameters:
        nomChanson (str): Path to the input video file.
        notes (list): List of musical notes corresponding to the detected pixels.
        gamme (int): Starting octave for the notes.
        vraiBpmChanson (int): Actual BPM of the song.
        pixelsSelectionnes (list): List of pixel coordinates to monitor for changes.
        tolerence (int): Tolerance threshold for detecting significant color changes.
        commencement (int): Index to start assigning notes from the `notes` list.
        valeurDeMultiplication (int): Multiplier for BPM conversion.
    """

    # Set up detection
    valeurDeMultiplication = 16
    tolerence = 100
    arrayPixel = []
    frameCorrection = -1
    bpmChanson = vraiBpmChanson * valeurDeMultiplication
    bpsChanson = bpmChanson / 60
    notes = ["C", "D", "E", "F", "G", "A", "B"]

    ordre_des_dieses = ["F#", "C#", "G#", "D#", "A#", "E#", "B#"]
    ordre_des_bemols = ["F-", "C-", "G-", "D-", "A-", "E-", "B-"]

    if nombreArmure > 0:
        a_modifier = ordre_des_dieses[:nombreArmure]
        for acc in a_modifier:
            note_base = acc[0]
            index = notes.index(note_base)
            notes[index] = acc
    elif nombreArmure < 0:
        nombreArmure = abs(nombreArmure)
        a_modifier = ordre_des_bemols[:nombreArmure]
        for acc in a_modifier:
            note_base = acc[0]
            index = notes.index(note_base)
            notes[index] = acc

    print("Notes modifiées :", notes)


    class Pixel:
        def __init__(self, coordonnee, valeurInitiale):
            self.coordonnee = coordonnee
            self.valeurInitiale = valeurInitiale
            self.note = None
            self.framesChangement = []

    # Fonction de rappel de la souris pour capturer les pixels sélectionnés
    def selectionnerPixel(event, x, y, flags, param):
        nonlocal pixelsSelectionnes, frame
        if event == cv2.EVENT_LBUTTONDOWN:
            pixelsSelectionnes.append((x, y))
            arrayPixel.append(Pixel((x, y), frame[y, x]))
            print(f"Pixel sélectionné : ({x}, {y}) avec valeur initiale : {frame[y, x]}")
            # Dessiner un cercle au pixel sélectionné
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
            cv2.imshow('Sélectionner Pixels', frame)

    def selectionnerPixelAuto():
        nonlocal pixelsSelectionnes, frame
        for pixelAuto in pixelsSelectionnes:
            x, y = pixelAuto
            arrayPixel.append(Pixel((x, y), frame[y, x]))
            print(f"Pixel sélectionné : ({x}, {y}) avec valeur initiale : {frame[y, x]}")

    def changerY():
        nonlocal pixelsSelectionnes
        for i in range(len(pixelsSelectionnes)):
            x, y = pixelsSelectionnes[i]
            y = 1
            pixelsSelectionnes[i] = (x, y)

    def pixelToNote():
        nonlocal arrayPixel, gamme
        compteur = commencement
        for pixel in arrayPixel:
            nomNote = notes[compteur]
            pixel.note = nomNote + str(gamme)
            compteur += 1
            if compteur > 6:
                compteur = 0
                gamme += 1

    def calculerDiff(valeurPrecedente, valeurActuelle, compteurFrame):
        r1, g1, b1 = valeurPrecedente
        r2, g2, b2 = valeurActuelle
        if (max(r1, r2) - min(r1, r2) > tolerence or max(g1, g2) - min(g1, g2) > tolerence or max(b1, b2) - min(b1,
                                                                                                                b2) > tolerence) and compteurFrame > frameCible and compteurFrame < 7479:
            return True
        return False

    def trouverValeurProche(valeurEntree):
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
    cap = cv2.VideoCapture(nomChanson)

    # Vérifier si la vidéo s'est ouverte correctement
    if not cap.isOpened():
        print("Erreur : Impossible d'ouvrir la vidéo.")
        return

    tauxFps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Taux de rafraîchissement de la vidéo : {tauxFps} FPS")

    # Lire les frames jusqu'à la frame cible
    compteurFrame = 0
    frameCible = 140
    frame = None

    while compteurFrame < frameCible:
        ret, frame = cap.read()
        if not ret:
            print("Erreur : Impossible de lire la frame.")
            return
        compteurFrame += 1

    if len(pixelsSelectionnes) > 0:
        selectionnerPixelAuto()

    # Afficher la frame cible et permettre à l'utilisateur de sélectionner des pixels
    cv2.imshow('Sélectionner Pixels', frame)
    cv2.setMouseCallback('Sélectionner Pixels', selectionnerPixel)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Vérifier si des pixels ont été sélectionnés
    if not pixelsSelectionnes:
        print("Aucun pixel sélectionné. Sortie.")
        return

    # Dictionnaire pour stocker les valeurs RVB précédentes des pixels sélectionnés
    valeursPrecedentes = {pixel: pixel.valeurInitiale for pixel in arrayPixel}

    pixelToNote()

    # Afficher chaque pixel et la note qui lui est attachée
    for pixel in arrayPixel:
        print(pixel.valeurInitiale)

    compteurFrame = 0

    # Réinitialiser la capture vidéo au début
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    noteApuuyerList = []
    # fluxMusical = stream.Score()
    # partieMusicale = stream.Part()
    #
    # fluxMusical.insert(0, tempo.MetronomeMark(vraiBpmChanson))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Traiter chaque pixel sélectionné
        for pixel in arrayPixel:
            x, y = pixel.coordonnee
            valeurActuelle = frame[y, x]
            valeurPrecedente = valeursPrecedentes[pixel]

            changementtt = calculerDiff(pixel.valeurInitiale, valeurActuelle, compteurFrame)

            if len(pixel.framesChangement) % 2 == 0:
                if changementtt:
                    if frameCorrection == -1:
                        frameCorrection = compteurFrame
                    pixel.framesChangement.append(compteurFrame)
                    print(
                        f"Changement significatif détecté à la frame {compteurFrame} pour le pixel {pixel.note} : Diff RVB = {np.sum(np.abs(valeurActuelle - valeurPrecedente))}")

            else:
                if not changementtt:
                    if frameCorrection == -1:
                        frameCorrection = compteurFrame
                    pixel.framesChangement.append(compteurFrame)
                    print(
                        f"Changement significatif détecté à la frame {compteurFrame} pour le pixel {pixel.note} : Diff RVB = {np.sum(np.abs(valeurActuelle - valeurPrecedente))}")

            # Mettre à jour la valeur précédente
            valeursPrecedentes[pixel] = valeurActuelle

        # Afficher la frame
        cv2.imshow('Frame', frame)

        # Interrompre la boucle si 'q' est pressé
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        compteurFrame += 1
        print(f"Frame traitée {compteurFrame}")

    # Libérer l'objet de capture vidéo
    cv2.destroyAllWindows()

    # Afficher les numéros de frame où chaque pixel a changé
    print("\nFrames où chaque pixel a changé :")
    for pixel in arrayPixel:
        print(f"Pixel {pixel.note} a changé dans les frames : {pixel.framesChangement}")

    frameCorrectionSpecialiser = frameCorrection

    for pixel in arrayPixel:
        noteApuuyerList.clear()
        compteur = 0
        changement = pixel.framesChangement
        print(pixel.note)
        for change in changement:
            if len(noteApuuyerList) == 0:
                noteApuuyerList.append(change)
            elif len(noteApuuyerList) == 1:
                noteApuuyerList.append(change)
                noteEnSecondes = (noteApuuyerList[1] - noteApuuyerList[0]) / tauxFps
                battement = noteEnSecondes * bpsChanson
                valeurProche = trouverValeurProche(battement)
                # instanceNote = note.Note(pixel.note)
                # instanceNote.quarterLength = valeurProche / valeurDeMultiplication
                decalageEnSecondes = (noteApuuyerList[0] - frameCorrection) / tauxFps
                decalageBattementEnSecondes = decalageEnSecondes * bpsChanson
                valeurProcheDecalageEnSecondes = trouverValeurProche(decalageBattementEnSecondes)
                # fluxMusical.coreInsert(valeurProcheDecalageEnSecondes / valeurDeMultiplication, instanceNote)
                noteApuuyerList.clear()

            compteur += 1

    # Libérer à nouveau l'objet de capture vidéo
    cap.release()
    cv2.destroyAllWindows()

    print("Pixel sélectionné")
    print(pixelsSelectionnes)

    # fluxMusical.write('midi', fp='score1111.mid')
