import cv2
import numpy as np
from music21 import *

# Set up video musique river flows in you
nomChanson = r"C:\Users\crina\Downloads\Yiruma - River Flows In You (Intermediate Piano Tutorial).mp4"
notes = ["C#", "D", "E", "F#", "G#", "A", "B"]
gamme = 1
vraiBpmChanson = 66
bpmChanson = vraiBpmChanson*16
bpsChanson = bpmChanson / 60

# Set up detection
pixelsSelectionnes = [(10, 291), (36, 251), (51, 293), (65, 293), (92, 242), (114, 243), (124, 292), (139, 289), (168, 247), (179, 293), (198, 292), (222, 247), (244, 252), (256, 297), (274, 289), (299, 254), (311, 294), (329, 291), (357, 257), (376, 253), (384, 291), (403, 286), (432, 248), (442, 289), (462, 290), (488, 257), (508, 259), (518, 291), (538, 292), (562, 254), (574, 288), (592, 292), (617, 254)]
arrayPixel = []
frameCorrection = -1
tolerence = 100
commencement = 6

# # Set up video musique fairytale
# nomChanson = r"C:\Users\crina\Downloads\Fairy Tail - Main Theme (Piano Version).mp4"
# notes = ["C", "D", "E", "F", "G", "A", "B-"]
# gamme = 1
# vraiBpmChanson = 120
# bpmChanson = vraiBpmChanson*16
# bpsChanson = bpmChanson / 60
#
# # Set up detection
# pixelsSelectionnes = [(32, 278), (42, 275), (57, 272), (70, 273), (79, 232), (93, 231), (103, 232), (114, 235), (129, 236), (144, 272), (157, 271), (169, 274), (181, 275), (192, 238), (206, 279), (218, 278), (231, 279), (244, 279), (256, 277), (270, 275), (280, 239), (293, 280), (307, 278), (321, 278), (332, 277), (344, 270), (357, 272), (367, 241), (379, 245), (394, 239), (408, 245), (420, 273), (432, 276), (446, 275), (454, 242), (468, 276), (480, 276), (495, 277), (505, 277), (518, 278), (528, 277), (540, 242), (553, 276), (565, 277), (578, 277), (588, 276), (601, 275), (611, 277), (623, 235)]
# arrayPixel = []
# frameCorrection = -1
# tolerence = 100
# commencement = 0


# # Set up video Imir
# nomChanson = r"C:\Users\crina\Downloads\Attack On Titan OST - Call of Silence (Ymir's Theme) (1).mp4"
# notes = ["C#", "D", "E", "F#", "G#", "A", "B"]
# gamme = 1
# vraiBpmChanson = 48
# bpmChanson = vraiBpmChanson*16
# bpsChanson = bpmChanson / 60
#
# # Set up detection
# pixelsSelectionnes = [(32, 221), (42, 277), (55, 276), (68, 229), (82, 230), (91, 280), (103, 279), (117, 230), (129, 227), (143, 235), (155, 231), (169, 231), (179, 164), (194, 235),(204, 233), (215, 253), (227, 277), (241, 234), (255, 234), (264, 277), (277, 276), (293, 238), (302, 277), (315, 277), (330, 232), (344, 232), (353, 227), (369, 228), (379, 197), (390, 224), (404, 277), (416, 232), (430, 232), (442, 277), (452, 277), (467, 236), (476, 273), (490, 275), (503, 230), (517, 233), (527, 276), (539, 273), (552, 234), (564, 276), (574, 276), (588, 231), (602, 233), (612, 276), (623, 273)]
# arrayPixel = []
# frameCorrection = -1
# tolerence = 100
# commencement = 0

# # Set up video Faded
# nomChanson = r"C:\Users\crina\Downloads\Alan Walker - Faded (Intermediate Piano Tutorial).mp4"
# notes = ["C-", "D-", "E-", "F", "G-", "A-", "B-"]
# gamme = 1
# vraiBpmChanson = 90
# bpmChanson = vraiBpmChanson*16
# bpsChanson = bpmChanson / 60
#
# # Set up detection
# pixelsSelectionnes = [(22, 286), (43, 256), (61, 254), (83, 293), (87, 257), (104, 257), (122, 257), (127, 293), (148, 261), (165, 264), (188, 289), (190, 265), (209, 265), (227, 265), (232, 293), (250, 264), (269, 265), (291, 289), (296, 258), (314, 253), (331, 256), (336, 289), (357, 251), (375, 253), (396, 296), (400, 262), (418, 263), (434, 264), (438, 291), (460, 250), (478, 254), (498, 294), (505, 264), (521, 263), (539, 264), (545, 294), (564, 253), (583, 253), (604, 296), (609, 256), (625, 257)]
# arrayPixel = []
# frameCorrection = -1
# tolerence = 100
# commencement = 0

class Pixel:
    def __init__(self, coordonnee, valeurInitiale):
        self.coordonnee = coordonnee
        self.valeurInitiale = valeurInitiale
        self.note = None
        self.framesChangement = []



# Fonction de rappel de la souris pour capturer les pixels sélectionnés
def selectionnerPixel(event, x, y, flags, param):
    global pixelsSelectionnes, frame
    if event == cv2.EVENT_LBUTTONDOWN:
        pixelsSelectionnes.append((x, y))
        arrayPixel.append( Pixel((x, y),frame[y, x]) )
        print(f"Pixel sélectionné : ({x}, {y}) avec valeur initiale : {frame[y, x]}")
        # Dessiner un cercle au pixel sélectionné
        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        cv2.imshow('Sélectionner Pixels', frame)

def selectionnerPixelAuto():
    global pixelsSelectionnes, valeursInitiales, frame
    # changerY()
    for pixelAuto in pixelsSelectionnes:
        x, y = pixelAuto
        arrayPixel.append(Pixel((x, y),frame[y, x]))
        print(f"Pixel sélectionné : ({x}, {y}) avec valeur initiale : {frame[y, x]}")

def changerY():
    global pixelsSelectionnes
    for i in range(len(pixelsSelectionnes)):
        x, y = pixelsSelectionnes[i]
        y = 1
        pixelsSelectionnes[i] = (x, y)

# Charger la vidéo
cap = cv2.VideoCapture(nomChanson)

# Vérifier si la vidéo s'est ouverte correctement
if not cap.isOpened():
    print("Erreur : Impossible d'ouvrir la vidéo.")
    exit()

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
        exit()
    compteurFrame += 1

if len(pixelsSelectionnes) > 0:
    selectionnerPixelAuto()


# # Vérifier si des pixels ont été sélectionnés précédemment
#     Dessiner des cercles autour des pixels précédemment sélectionnés
# print(pixelsSelectionnes)
# for pixel in pixelsSelectionnes:
#     cv2.circle(frame, pixel, 2, (0, 255, 0), -1)


# Afficher la frame cible et permettre à l'utilisateur de sélectionner des pixels
cv2.imshow('Sélectionner Pixels', frame)
cv2.setMouseCallback('Sélectionner Pixels', selectionnerPixel)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Vérifier si des pixels ont été sélectionnés
if not pixelsSelectionnes:
    print("Aucun pixel sélectionné. Sortie.")
    exit()



# Dictionnaire pour stocker les valeurs RVB précédentes des pixels sélectionnés
valeursPrecedentes = {pixel: pixel.valeurInitiale for pixel in arrayPixel}


def pixelToNote():
    global arrayPixel, gamme
    compteur = commencement
    for pixel in arrayPixel:
        nomNote = notes[compteur]
        pixel.note = nomNote + str(gamme)
        compteur += 1
        if compteur > 6:
            compteur = 0
            gamme += 1

pixelToNote()

# Afficher chaque pixel et la note qui lui est attachée
for pixel in arrayPixel:
    print(pixel.valeurInitiale)

def calculerDiff(valeurPrecedente, valeurActuelle, compteurFrame):
    r1, g1, b1 = valeurPrecedente
    r2, g2, b2 = valeurActuelle
    if (max(r1, r2) - min(r1, r2) > tolerence or max(g1, g2) - min(g1, g2) > tolerence or max(b1, b2) - min(b1, b2) > tolerence) and compteurFrame > frameCible and compteurFrame<7479:
        # print(valeurPrecedente)
        # print(valeurActuelle)
        return True
    return False

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
            instanceNote = note.Note(pixel.note)
            instanceNote.quarterLength = valeurProche/16
            decalageEnSecondes = (noteApuuyerList[0] - frameCorrection) / tauxFps
            decalageBattementEnSecondes = decalageEnSecondes * bpsChanson
            valeurProcheDecalageEnSecondes = trouverValeurProche(decalageBattementEnSecondes)
            # print(noteApuuyerList[1])
            # print(noteApuuyerList[2])
            # print("battement = ")
            # print(battement)
            # print("Battement corriger = ")
            # print(valeurProche)
            # print("Decalage = ")
            # print(decalageBattementEnSecondes)
            # print("decalage formater = ")
            # print(valeurProcheDecalageEnSecondes)
            # print("frame correction = ")
            # print(frameCorrectionSpecialiser)
            # frameCorrectionSpecialiser = (frameCorrection + (fluxMusical.quarterLength / bpsChanson * tauxFps)) - noteApuuyerList[2]
            fluxMusical.coreInsert(valeurProcheDecalageEnSecondes/16, instanceNote)
            noteApuuyerList.clear()

        compteur += 1

fluxMusical.insert(0, tempo.MetronomeMark(vraiBpmChanson))

# Afficher les frames où des changements se sont produits
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

print("Pixel sélectionné")
print(pixelsSelectionnes)

fluxMusical.write('midi', fp='score0001.mid')
# fluxMusical.show("midi")
