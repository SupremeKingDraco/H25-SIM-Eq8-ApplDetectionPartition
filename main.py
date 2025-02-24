# import cv2
# import numpy as np
# from music21 import *
#
# # Global variables to store selected pixels and their initial values
# notes = ["C","D","E","F","G","A","B"]
# gamme = 4
# selected_pixels = [(8, 302), (51, 299), (91, 299), (114, 297), (153, 294), (197, 294), (233, 294), (251, 296), (294, 297), (335, 297), (356, 297), (398, 298), (438, 298), (477, 300), (500, 300), (540, 299), (578, 299), (600, 299)]
# initial_values = {}
# selected_pixels_note = {}
# bpm_song = 86
# bps_song = bpm_song / 60
#
# # Mouse callback function to capture selected pixels
# def select_pixel(event, x, y, flags, param):
#     global selected_pixels, initial_values
#     if event == cv2.EVENT_LBUTTONDOWN:
#         selected_pixels.append((x, y))
#         initial_values[(x, y)] = frame[y, x]
#         print(f"Selected pixel: ({x}, {y}) with initial value: {frame[y, x]}")
#         # Draw a circle at the selected pixel
#         cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
#         cv2.imshow('Select Pixels', frame)
#
# def select_pixel_auto():
#     global selected_pixels, initial_values, frame
#     # change_y()
#     for pixelauto in selected_pixels:
#         x, y = pixelauto
#         initial_values[(x, y)] = frame[y, x]
#         print(f"Selected pixel: ({x}, {y}) with initial value: {frame[y, x]}")
#
# def change_y():
#     global selected_pixels
#     for i in range(len(selected_pixels)):
#         x,y = selected_pixels[i]
#         y = 15
#         selected_pixels[i] = (x,y)
#
# # Load the video
# video_path = r"C:\Users\crina\Downloads\videoplayback.mp4"
# cap = cv2.VideoCapture(video_path)
#
# # Check if the video opened successfully
# if not cap.isOpened():
#     print("Error: Could not open video.")
#     exit()
#
# frame_rate = cap.get(cv2.CAP_PROP_FPS)
# print(f"Frame rate of the video: {frame_rate} FPS")
#
# # Read frames until the target frame
# frame_count = 0
# target_frame = 1
# frame = None
#
# while frame_count < target_frame:
#     ret, frame = cap.read()
#     if not ret:
#         print("Error: Could not read the frame.")
#         exit()
#     frame_count += 1
#
# if len(selected_pixels)>0:
#     select_pixel_auto()
#
# # Check if any pixels were selected previously
# if not selected_pixels:
#     # Display the target frame and allow the user to select pixels
#     cv2.imshow('Select Pixels', frame)
#     cv2.setMouseCallback('Select Pixels', select_pixel)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#
#     # Check if any pixels were selected
#     if not selected_pixels:
#         print("No pixels selected. Exiting.")
#         exit()
# else:
#     # Draw circles around previously selected pixels
#     for pixel in selected_pixels:
#         cv2.circle(frame, pixel, 5, (0, 255, 0), -1)
#     cv2.imshow('Selected Pixels', frame)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#
# # Dictionary to store the previous RGB values of the selected pixels
# previous_values = {pixel: initial_values[pixel] for pixel in selected_pixels}
#
# counter = 0
# for pixel in selected_pixels:
#     note_name = notes[counter]
#     selected_pixels_note[pixel] = note_name + str(gamme)
#     counter += 1
#     if counter > 6:
#         counter = 0
#         gamme += 1
#
# # Print each pixel and note that's attached to it
# for pixel in selected_pixels:
#     print(selected_pixels_note[pixel])
#
# def calculer_diff(previous_value, current_value, frame_count):
#     r1, g1, b1 = previous_value
#     r2, g2, b2 = current_value
#     if (max(r1, r2) - min(r1, r2) > 50 or max(g1, g2) - min(g1, g2) > 50 or max(b1, b2) - min(b1, b2) > 50) and frame_count > 10:
#         return True
#     return False
#
# # Dictionary to store frame numbers where each pixel changed
# change_frames = {pixel: [] for pixel in selected_pixels}
#
# frame_count = 0
#
# # Reset the video capture to the beginning
# cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
#
# lenght = []
# music_stream = stream.Stream()
#
# def find_closest_value(input_value):
#     # Define the multiples
#     multiple_0_25 = 0.25
#     multiple_1_3 = 1 / 3
#
#     # Check if the value is close to zero
#     if abs(input_value) < 0.01:
#         return 0.0
#
#     # Calculate the nearest multiples
#     nearest_0_125 = round(input_value / multiple_0_25) * multiple_0_25
#     nearest_1_3 = round(input_value / multiple_1_3) * multiple_1_3
#
#     # Determine which multiple is closer
#     if abs(input_value - nearest_0_125) < abs(input_value - nearest_1_3):
#         closest_value = nearest_0_125
#     else:
#         closest_value = nearest_1_3
#
#     # Round the result to three decimal places
#     return round(closest_value, 3)
#
# processed_pixel = None
#
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break
#
#     if len(lenght)>0:
#         pixelss = lenght[0]
#         x, y = pixelss
#         current_value = frame[y, x]
#         previous_value = previous_values[pixelss]
#         if calculer_diff(previous_value, current_value, frame_count):
#             lenght.append(frame_count)
#             note_pushed = lenght[2] - lenght[1]
#             note_in_second = (note_pushed / frame_rate) * bps_song
#             closest_value = find_closest_value(note_in_second)
#             note_instance = note.Note(selected_pixels_note[lenght[0]])
#             note_instance.quarterLength = closest_value
#             print(note_instance)
#             music_stream.append(note_instance)
#             processed_pixel = lenght[0]
#             lenght.clear()
#
#     # Process each selected pixel
#     for pixel in selected_pixels:
#         x, y = pixel
#         current_value = frame[y, x]
#         previous_value = previous_values[pixel]
#
#
#         if calculer_diff(previous_value, current_value, frame_count):
#             if len(lenght) == 0 and pixel != processed_pixel:
#                 processed_pixel= None
#                 lenght.append(pixel)
#                 lenght.append(frame_count)
#
#
#             change_frames[pixel].append(frame_count)
#             print(f"Significant change detected at frame {frame_count} for pixel {pixel}: RGB diff = {np.sum(np.abs(current_value - previous_value))}")
#
#         # Update the previous value
#         previous_values[pixel] = current_value
#
#     # Display the frame
#     cv2.imshow('Frame', frame)
#
#     # Break the loop if 'q' is pressed
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
#     processed_pixel = None
#     frame_count += 1
#     print(f"Processed frame {frame_count}")
#
# music_stream.insert(0, tempo.MetronomeMark(bpm_song))
#
# # Release the video capture object
# cv2.destroyAllWindows()
#
# # Print the frame numbers where each pixel changed
# print("\nFrames where each pixel changed:")
# for pixel, frames in change_frames.items():
#     print(f"Pixel {pixel} changed in frames: {frames}")
#
# # Display the frames where changes occurred
# # for pixel, frames in change_frames.items():
# #     print(f"\nDisplaying frames where pixel {pixel} changed:")
# #     for frame_number in frames:
# #         cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
# #         ret, frame = cap.read()
# #         if ret:
# #             cv2.imshow(f'Frame {frame_number} - Pixel {pixel}', frame)
# #             cv2.waitKey(0)  # Wait for a key press to close the window
# #         else:
# #             print(f"Error: Could not read frame {frame_number}")
#
# # Release the video capture object again
# cap.release()
# cv2.destroyAllWindows()
# music_stream.show()
#
#






import cv2
import numpy as np
from music21 import stream,chord,tempo,note

# Variables globales pour stocker les pixels sélectionnés et leurs valeurs initiales
notes = ["C", "D", "E", "F", "G", "A", "B"]
gamme = 4
pixelsSelectionnes = []
valeursInitiales = {}
pixelsSelectionnesNote = {}
bpmChanson = 86
bpsChanson = bpmChanson / 60

# Fonction de rappel de la souris pour capturer les pixels sélectionnés
def selectionnerPixel(event, x, y, flags, param):
    global pixelsSelectionnes, valeursInitiales, frame
    if event == cv2.EVENT_LBUTTONDOWN:
        pixelsSelectionnes.append((x, y))
        valeursInitiales[(x, y)] = frame[y, x]
        print(f"Pixel sélectionné : ({x}, {y}) avec valeur initiale : {frame[y, x]}")
        # Dessiner un cercle au pixel sélectionné
        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        cv2.imshow('Sélectionner Pixels', frame)

def selectionnerPixelAuto():
    global pixelsSelectionnes, valeursInitiales, frame
    # changerY()
    for pixelAuto in pixelsSelectionnes:
        x, y = pixelAuto
        valeursInitiales[(x, y)] = frame[y, x]
        print(f"Pixel sélectionné : ({x}, {y}) avec valeur initiale : {frame[y, x]}")

def changerY():
    global pixelsSelectionnes
    for i in range(len(pixelsSelectionnes)):
        x, y = pixelsSelectionnes[i]
        y = 15
        pixelsSelectionnes[i] = (x, y)

# Charger la vidéo
cheminVideo = r"C:\Users\crina\Downloads\videoplayback.mp4"
cap = cv2.VideoCapture(cheminVideo)

# Vérifier si la vidéo s'est ouverte correctement
if not cap.isOpened():
    print("Erreur : Impossible d'ouvrir la vidéo.")
    exit()

tauxFps = cap.get(cv2.CAP_PROP_FPS)
print(f"Taux de rafraîchissement de la vidéo : {tauxFps} FPS")

# Lire les frames jusqu'à la frame cible
compteurFrame = 0
frameCible = 1
frame = None

while compteurFrame < frameCible:
    ret, frame = cap.read()
    if not ret:
        print("Erreur : Impossible de lire la frame.")
        exit()
    compteurFrame += 1

if len(pixelsSelectionnes) > 0:
    selectionnerPixelAuto()

# Vérifier si des pixels ont été sélectionnés précédemment
if not pixelsSelectionnes:
    # Afficher la frame cible et permettre à l'utilisateur de sélectionner des pixels
    cv2.imshow('Sélectionner Pixels', frame)
    cv2.setMouseCallback('Sélectionner Pixels', selectionnerPixel)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Vérifier si des pixels ont été sélectionnés
    if not pixelsSelectionnes:
        print("Aucun pixel sélectionné. Sortie.")
        exit()
else:
    # Dessiner des cercles autour des pixels précédemment sélectionnés
    for pixel in pixelsSelectionnes:
        cv2.circle(frame, pixel, 2, (0, 255, 0), -1)
    cv2.imshow('Pixels Sélectionnés', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Dictionnaire pour stocker les valeurs RVB précédentes des pixels sélectionnés
valeursPrecedentes = {pixel: valeursInitiales[pixel] for pixel in pixelsSelectionnes}

compteur = 0
for pixel in pixelsSelectionnes:
    nomNote = notes[compteur]
    pixelsSelectionnesNote[pixel] = nomNote + str(gamme)
    compteur += 1
    if compteur > 6:
        compteur = 0
        gamme += 1

# Afficher chaque pixel et la note qui lui est attachée
for pixel in pixelsSelectionnes:
    print(pixelsSelectionnesNote[pixel])

def calculerDiff(valeurPrecedente, valeurActuelle, compteurFrame):
    r1, g1, b1 = valeurPrecedente
    r2, g2, b2 = valeurActuelle
    if (max(r1, r2) - min(r1, r2) > 8 or max(g1, g2) - min(g1, g2) > 8 or max(b1, b2) - min(b1, b2) > 8) and compteurFrame > frameCible:
        print(valeurPrecedente)
        print(valeurActuelle)
        return True
    return False

# Dictionnaire pour stocker les numéros de frame où chaque pixel a changé
framesChangement = {pixel: [] for pixel in pixelsSelectionnes}

compteurFrame = 0

# Réinitialiser la capture vidéo au début
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

noteApuuyerList = []
fluxMusical = stream.Score()
partieMusicale = stream.Part()

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

print("Pixel sélectionné")
print(pixelsSelectionnes)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Traiter chaque pixel sélectionné
    for pixel in pixelsSelectionnes:
        x, y = pixel
        valeurActuelle = frame[y, x]
        valeurPrecedente = valeursPrecedentes[pixel]

        if calculerDiff(valeurPrecedente, valeurActuelle, compteurFrame):
            framesChangement[pixel].append(compteurFrame)
            print(f"Changement significatif détecté à la frame {compteurFrame} pour le pixel {pixel} : Diff RVB = {np.sum(np.abs(valeurActuelle - valeurPrecedente))}")

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
for pixel, frames in framesChangement.items():
    print(f"Pixel {pixelsSelectionnesNote[pixel]} a changé dans les frames : {frames}")

for pixel in pixelsSelectionnes:
    noteApuuyerList.clear()
    compteur = 0
    changement = framesChangement[pixel]
    print(pixelsSelectionnesNote[pixel])
    for changement in changement:
        if len(noteApuuyerList) == 0:
            noteApuuyerList.append(pixel)
            noteApuuyerList.append(changement)
        elif len(noteApuuyerList) == 2:
            noteApuuyerList.append(changement)
            noteEnSecondes = (noteApuuyerList[2] - noteApuuyerList[1]) / tauxFps
            battement = noteEnSecondes * bpsChanson
            valeurProche = trouverValeurProche(battement)
            instanceNote = note.Note(pixelsSelectionnesNote[noteApuuyerList[0]])
            instanceNote.quarterLength = valeurProche
            decalageEnSecondes = (noteApuuyerList[1] - 90) / tauxFps
            decalageBattementEnSecondes = decalageEnSecondes * bpsChanson
            valeurProcheDecalageEnSecondes = trouverValeurProche(decalageBattementEnSecondes)
            print(noteApuuyerList[1])
            print(noteApuuyerList[2])
            if valeurProche< 10:
                fluxMusical.insertIntoNoteOrChord(valeurProcheDecalageEnSecondes, instanceNote)
            noteApuuyerList.clear()

        compteur += 1

fluxMusical.insert(0, tempo.MetronomeMark(bpmChanson))

# # Afficher les frames où des changements se sont produits
# for pixel, frames in framesChangement.items():
#     print(f"\nAffichage des frames où le pixel {pixelsSelectionnesNote[pixel]} a changé :")
#     for numeroFrame in frames:
#         cap.set(cv2.CAP_PROP_POS_FRAMES, numeroFrame)
#         ret, frame = cap.read()
#         if ret:
#             cv2.imshow(f'Frame {numeroFrame} - Pixel {pixelsSelectionnesNote[pixel]}', frame)
#             cv2.waitKey(0)  # Attendre un appui sur une touche pour fermer la fenêtre
#         else:
#             print(f"Erreur : Impossible de lire la frame {numeroFrame}")

# Libérer à nouveau l'objet de capture vidéo
cap.release()
cv2.destroyAllWindows()


fluxMusical.write('midi', fp='score0000.mid')
# fluxMusical.show()
