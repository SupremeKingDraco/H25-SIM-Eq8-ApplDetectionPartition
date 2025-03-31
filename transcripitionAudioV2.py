import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import os
from music21.tempo import MetronomeMark
from music21 import *
import moviepy.editor as mp
from scipy.signal import find_peaks

# Extraire l'audio de la vidéo
nomVideo = mp.VideoFileClip(r"C:\Users\TheBr\Downloads\Yiruma_-_River_Flows_In_You_Intermediate_Piano_Tutorial.mp4")
nomVideo.audio.write_audiofile(r"C:\Users\TheBr\Downloads\versionAudio.mp3")

# Configuration du chemin du fichier
cheminFichier = r"C:\Users\TheBr\Downloads"
nomFichier = os.path.join(cheminFichier, "versionAudio.mp3")

# Paramètres
frequenceEchantillonnage = 44100  # Taux d'échantillonnage
longueurFft = 2048  # Longueur de la fenêtre FFT
recouvrement = 0.5  # Pourcentage de recouvrement
longueurSaut = int(longueurFft * (1 - recouvrement))  # Longueur de saut
nombreBins = 72  # Nombre de bandes de fréquence
exposantMagnitude = 4  # Exposant de magnitude
seuilDb = -61  # Seuil de silence en dB

# Vérifier si le fichier existe
if not os.path.exists(nomFichier):
    print(f"Erreur : le fichier '{nomFichier}' n'existe pas.")
else:
    print(f"Fichier '{nomFichier}' trouvé. Chargement en cours...")
    signalAudio, frequenceEchantillonnage = librosa.load(nomFichier)

    # Trouver le tempo du morceau
    tempo, framesBattements = librosa.beat.beat_track(y=signalAudio, sr=frequenceEchantillonnage)
    tempo = tempo.item()
    tempo = int(2 * round(tempo / 2))  # Arrondi au nombre pair le plus proche
    metronome = MetronomeMark(referent='quarter', number=tempo)  # Création de l'objet MetronomeMark

    # Calcul de la STFT et conversion de la magnitude en décibels
    D = librosa.stft(signalAudio, n_fft=longueurFft, hop_length=longueurSaut)
    magnitudeDb = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    frequences = librosa.fft_frequencies(sr=frequenceEchantillonnage, n_fft=2048)

    # Estimer la hauteur pour chaque trame
    estimationPitch = [find_peaks(magnitudeDb[:, i], height=-15)[0] for i in range(magnitudeDb.shape[1])]

    # Convertir les fréquences en noms de notes
    def pitchVersNote(pitch):
        if pitch <= 0:
            return 'silence'
        noteMidi = librosa.hz_to_midi(pitch)
        nomNote = librosa.midi_to_note(noteMidi)

        # Remplacer les altérations Unicode par des équivalents ASCII
        nomNote = nomNote.replace('♯', '#').replace('♭', 'b')
        return nomNote

    notesDetectees = [[pitchVersNote(frequences[p]) for p in frame] for frame in estimationPitch]

    # Debug : Afficher les notes détectées
    print("Notes détectées :", notesDetectees)

    # Création de la partition et de la partie
    partitionMusicale = stream.Score()
    partieMusicale = stream.Part()
    partieMusicale.append(metadata.Metadata(title='Transcription Audio', composer='Transcription Automatique'))

    # Traiter les trames et insérer les notes/silences
    notesActuelles = set()
    compteurNotes = {}
    dureeTrame = 2048 * 0.5 / frequenceEchantillonnage
    dureeMinimale = 0.125

    for i, trameNotes in enumerate(notesDetectees):
        decalageTemps = i * dureeTrame

        # Gérer les notes terminées
        notesTerminees = notesActuelles - set(trameNotes)
        for noteTerminee in notesTerminees:
            dureeNote = compteurNotes.pop(noteTerminee, 0) * dureeTrame
            if dureeNote > 0:
                if noteTerminee == 'silence':
                    noteSilence = note.Rest(quarterLength=max(dureeNote, dureeMinimale))
                    partieMusicale.insert(decalageTemps - dureeNote, noteSilence)
                else:
                    noteMusicale = note.Note(noteTerminee)
                    noteMusicale.quarterLength = max(dureeNote, dureeMinimale)
                    partieMusicale.insert(decalageTemps - dureeNote, noteMusicale)

        # Gérer les nouvelles notes
        nouvellesNotes = set(trameNotes) - notesActuelles
        for nouvelleNote in nouvellesNotes:
            compteurNotes[nouvelleNote] = 0

        # Mettre à jour les compteurs des notes actives
        for noteActive in notesActuelles.intersection(trameNotes):
            compteurNotes[noteActive] += 1

        # Mettre à jour notesActuelles
        notesActuelles = set(trameNotes)

        # Gérer les silences
        if not trameNotes:
            noteSilence = note.Rest(quarterLength=dureeMinimale)
            partieMusicale.insert(decalageTemps, noteSilence)

    # Finaliser la sortie MIDI
    if len(partieMusicale.notesAndRests) > 0:
        partitionMusicale.append(partieMusicale)
        cheminMidi = 'partition0010.mid'
        partitionMusicale.write('midi', fp=cheminMidi)
        print(f"Fichier MIDI écrit à {cheminMidi}")
    else:
        print("Erreur : aucune note ou silence trouvé dans la partition.")
