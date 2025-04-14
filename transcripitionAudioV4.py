import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import os
from music21.tempo import MetronomeMark
from music21 import *
import moviepy.editor as mp
from scipy.signal import find_peaks, butter, filtfilt, medfilt

def extraire_audio(nomVideo, cheminFichier, nomFichier):
    # Extraire l'audio de la vidéo et l'enregistrer sous forme de fichier MP3.
    video = mp.VideoFileClip(nomVideo)
    video.audio.write_audiofile(nomFichier)

def charger_fichier_audio(nomFichier, frequenceEchantillonnage=44100):
    # Charger le fichier audio et retourner le signal audio et la fréquence d'échantillonnage.
    if not os.path.exists(nomFichier):
        raise FileNotFoundError(f"Erreur : le fichier '{nomFichier}' n'existe pas.")
    return librosa.load(nomFichier, sr=frequenceEchantillonnage)

def detecter_tempo(signalAudio, frequenceEchantillonnage):
    # Détecter le tempo du morceau audio

    tempo, framesBattements = librosa.beat.beat_track(y=signalAudio, sr=frequenceEchantillonnage)
    tempo = tempo.item()
    tempo = int(2 * round(tempo / 2))  # Arrondi au nombre pair le plus proche
    return MetronomeMark(referent='quarter', number=tempo)

def butter_lowpass(cutoff, fs, order=5):
    # Conception d'un filtre passe-bas Butterworth.
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def lowpass_filter(data, cutoff, fs, order=5):
    # Application d'un filtre passe-bas
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def appliquer_filtres(signalAudio, frequenceEchantillonnage, cutoff_frequency=4186, kernel_size=5):
    # Appliquer les filtres passe-bas et médian au signal audio
    filtered_signal = lowpass_filter(signalAudio, cutoff_frequency, frequenceEchantillonnage)
    filtered_signal = medfilt(filtered_signal, kernel_size=kernel_size)
    return filtered_signal

def estimer_hauteur(filtered_signal, frequenceEchantillonnage, longueurFft, longueurSaut, seuilDb):
    # Estimer la hauteur (pitch) pour chaque trame du signal audio
    D = librosa.stft(filtered_signal, n_fft=longueurFft, hop_length=longueurSaut)
    magnitudeDb = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    frequences = librosa.fft_frequencies(sr=frequenceEchantillonnage, n_fft=longueurFft)

    estimationPitch = []
    for i in range(magnitudeDb.shape[1]):
        peaks, _ = find_peaks(magnitudeDb[:, i], height=seuilDb)
        estimationPitch.append(peaks)

    return estimationPitch, frequences, magnitudeDb

def pitchVersNote(pitch, frequences):
    # Convertir une fréquence en nom de note.
    if pitch <= 0:
        return 'silence'
    noteMidi = librosa.hz_to_midi(pitch)
    nomNote = librosa.midi_to_note(noteMidi)
    return nomNote.replace('♯', '#').replace('♭', 'b')

def creer_partition(estimationPitch, frequences, frequenceEchantillonnage, longueurFft, longueurSaut):
    #Créer une partition musicale à partir des hauteurs estimées
    notesDetectees = [[pitchVersNote(frequences[p], frequences) for p in frame] for frame in estimationPitch]
    partitionMusicale = stream.Score()
    partieMusicale = stream.Part()
    partieMusicale.append(metadata.Metadata(title='Transcription Audio', composer='Transcription Automatique'))

    notesActuelles = set()
    compteurNotes = {}
    dureeTrame = longueurFft * 0.5 / frequenceEchantillonnage
    dureeMinimale = 0.125

    for i, trameNotes in enumerate(notesDetectees):
        decalageTemps = i * dureeTrame

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

        nouvellesNotes = set(trameNotes) - notesActuelles
        for nouvelleNote in nouvellesNotes:
            compteurNotes[nouvelleNote] = 0

        for noteActive in notesActuelles.intersection(trameNotes):
            compteurNotes[noteActive] += 1

        notesActuelles = set(trameNotes)

        if not trameNotes:
            noteSilence = note.Rest(quarterLength=dureeMinimale)
            partieMusicale.insert(decalageTemps, noteSilence)

    if len(partieMusicale.notesAndRests) > 0:
        partitionMusicale.append(partieMusicale)
        cheminMidi = 'partition0010.mid'
        partitionMusicale.write('midi', fp=cheminMidi)
        print(f"Fichier MIDI écrit à {cheminMidi}")
    else:
        print("Erreur : aucune note ou silence trouvé dans la partition.")

def visualiser_spectrogramme(magnitudeDb, frequenceEchantillonnage, longueurSaut, estimationPitch, longueurFft):
    plt.figure(figsize=(12, 6))
    librosa.display.specshow(magnitudeDb, sr=frequenceEchantillonnage, hop_length=longueurSaut, x_axis='time',
                             y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogramme avec Pics Détectés')

    # Tracer les pics détectés
    for i, peaks in enumerate(estimationPitch):
        for peak in peaks:
            plt.plot(i * longueurSaut / frequenceEchantillonnage,
                     librosa.fft_frequencies(sr=frequenceEchantillonnage)[peak], 'ro')

    plt.tight_layout()
    plt.show()

def main(nomVideo, cheminFichier, nomFichier, longueurFft, recouvrement, seuilDb):
    extraire_audio(nomVideo, cheminFichier, nomFichier)
    signalAudio, frequenceEchantillonnage = charger_fichier_audio(nomFichier)
    tempo = detecter_tempo(signalAudio, frequenceEchantillonnage)


    longueurSaut = int(longueurFft * (1 - recouvrement))
    filtered_signal = appliquer_filtres(signalAudio, frequenceEchantillonnage)
    estimationPitch, frequences, magnitudeDb = estimer_hauteur(filtered_signal, frequenceEchantillonnage, longueurFft, longueurSaut, seuilDb)
    creer_partition(estimationPitch, frequences, frequenceEchantillonnage, longueurFft, longueurSaut)
    visualiser_spectrogramme(magnitudeDb, frequenceEchantillonnage, longueurSaut, estimationPitch, longueurFft)

# Exemple d'utilisation
nomVideo = r"C:\Users\TheBr\Downloads\Yiruma_-_River_Flows_In_You_Intermediate_Piano_Tutorial.mp4"
cheminFichier = r"C:\Users\TheBr\Downloads"
nomFichier = os.path.join(cheminFichier, "versionAudio.mp3")
longueurFft = 2048
recouvrement = 0.5
seuilDb = -15


def run():
    main(nomVideo, cheminFichier, nomFichier, longueurFft, recouvrement, seuilDb)
