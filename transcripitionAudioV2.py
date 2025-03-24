import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import os
from music21.tempo import MetronomeMark
from music21 import *
import moviepy.editor as mp
from scipy.signal import find_peaks

# Extraction de l'audio depuis la vidéo
print("Extraction de l'audio depuis la vidéo...")
clipVideo = mp.VideoFileClip(r"C:\Users\TheBr\Downloads\Yiruma_-_River_Flows_In_You_Intermediate_Piano_Tutorial.mp4")
clipVideo.audio.write_audiofile(r"C:\Users\TheBr\Downloads\versionAudio.mp3")

# Chemin vers le fichier audio extrait
cheminBase = r"C:\Users\TheBr\Downloads"
fichierAudio = os.path.join(cheminBase, "versionAudio.mp3")

# Vérifier si le fichier audio existe
if not os.path.exists(fichierAudio):
    print(f"Erreur : Le fichier '{fichierAudio}' n'existe pas.")
else:
    print(f"Fichier trouvé : '{fichierAudio}'. Chargement en cours...")
    donneesAudio, frequenceEchantillonnage = librosa.load(fichierAudio)

    # Détection du tempo de la pièce
    print("Détection du tempo...")
    valeurTempo, _ = librosa.beat.beat_track(y=donneesAudio, sr=frequenceEchantillonnage)
    valeurTempo = int(round(valeurTempo / 2))  # Arrondir au BPM le plus proche
    print(f"Tempo détecté : {valeurTempo} BPM")
    marqueTempo = MetronomeMark(referent='quarter', number=valeurTempo)  # Créer un marqueur de tempo

    # Analyse spectrale pour détecter les notes
    print("Analyse spectrale en cours...")
    matriceStft = librosa.stft(donneesAudio, n_fft=2048, hop_length=int(2048 * 0.5))  # Calcul de la STFT
    magnitudeDecibels = librosa.amplitude_to_db(np.abs(matriceStft), ref=np.max)  # Conversion en décibels
    frequencesHz = librosa.fft_frequencies(sr=frequenceEchantillonnage, n_fft=2048)  # Fréquences correspondantes

    # Fonction pour convertir une fréquence en note musicale
    def frequenceVersNote(frequence):
        if frequence <= 0:
            return 'silence'
        noteMidi = librosa.hz_to_midi(frequence)
        nomNote = librosa.midi_to_note(noteMidi)
        # Remplacer les symboles Unicode par des équivalents ASCII
        nomNote = nomNote.replace('♯', '#').replace('♭', 'b')
        return nomNote

    # Détecter les pics de fréquence pour chaque fenêtre temporelle
    notesDetectees = []
    for i in range(magnitudeDecibels.shape[1]):
        pics, _ = find_peaks(magnitudeDecibels[:, i], height=-15)  # Trouver les pics significatifs
        notesFenetre = [frequenceVersNote(frequencesHz[p]) for p in pics]
        notesDetectees.append(notesFenetre)

    print("Notes détectées :", notesDetectees)

    # Création de la partition MIDI
    print("Création de la partition MIDI")
    partition = stream.Score()  # Créer une nouvelle partition
    partie = stream.Part()  # Créer une nouvelle partie
    partie.insert(0, marqueTempo)  # Ajouter le tempo à la partition

    # Initialiser les variables pour suivre les notes actives
    notesActives = set()
    dureesNotes = {}
    dureeTrame = 2048 * 0.5 / frequenceEchantillonnage  # Durée d'une trame en secondes
    dureeMinimale = 0.125  # Durée minimale d'une note ou d'un silence

    for i, notesFenetre in enumerate(notesDetectees):
        tempsActuel = i * dureeTrame

        # Gérer les notes qui se terminent
        notesTerminees = notesActives - set(notesFenetre)
        for note in notesTerminees:
            duree = dureesNotes.pop(note, 0) * dureeTrame
            if duree > 0:
                if note == 'silence':
                    silence = note.Rest(quarterLength=max(duree, dureeMinimale))
                    partie.insert(tempsActuel - duree, silence)
                else:
                    noteMusicale = note.Note(note)
                    noteMusicale.quarterLength = max(duree, dureeMinimale)
                    partie.insert(tempsActuel - duree, noteMusicale)

        # Gérer les nouvelles notes
        nouvellesNotes = set(notesFenetre) - notesActives
        for nouvelleNote in nouvellesNotes:
            dureesNotes[nouvelleNote] = 0

        # Mettre à jour les compteurs pour les notes actives
        for noteActive in notesActives.intersection(notesFenetre):
            dureesNotes[noteActive] += 1

        # Mettre à jour les notes actives
        notesActives = set(notesFenetre)

        # Ajouter un silence si aucune note n'est détectée
        if not notesFenetre:
            silence = note.Rest(quarterLength=dureeMinimale)
            partie.insert(tempsActuel, silence)

    # Finaliser la partition
    if len(partie.notesAndRests) > 0:
        partition.append(partie)
        cheminMidi = 'partitionFinale.mid'
        partition.write('midi', fp=cheminMidi)
        print(f"Fichier MIDI créé : {cheminMidi}")
    else:
        print("Erreur : Aucune note ou silence trouvé dans la partition.")