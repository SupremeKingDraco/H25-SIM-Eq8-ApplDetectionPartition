import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import os
from music21.tempo import MetronomeMark
from music21 import *
import moviepy.editor as mp
from scipy.signal import find_peaks, butter, filtfilt, medfilt

# Constantes
longueurFft = 2048
recouvrement = 0.5

def extraire_audio(path_video, path_fichier_audio):
    # Extraire l'audio de la vidéo et l'enregistrer sous forme de fichier MP3
    video = mp.VideoFileClip(path_video)
    video.audio.write_audiofile(path_fichier_audio)

def charger_fichier_audio(nom_fichier, frequence_echantillonnage=44100):
    # Charger le fichier audio et retourner le signal audio et la fréquence d'échantillonnage
    if not os.path.exists(nom_fichier):
        raise FileNotFoundError(f"Erreur : le fichier '{nom_fichier}' n'existe pas.")
    return librosa.load(nom_fichier, sr=frequence_echantillonnage)

def detecter_tempo(signal_audio, frequence_echantillonnage):
    # Détecter le tempo

    tempo, frames_battements = librosa.beat.beat_track(y=signal_audio, sr=frequence_echantillonnage)
    tempo = tempo.item()
    tempo = int(2 * round(tempo / 2))  # Arrondi au nombre pair le plus proche
    return MetronomeMark(referent='quarter', number=tempo)

def butter_passe_bas(cutoff, fs, order=5):
    # Application d'un filtre passe-bas Butterworth.
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def filtre_pass_bas(data, cutoff, fs, order=5):
    # Application d'un filtre passe-bas.
    b, a = butter_passe_bas(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def appliquer_filtres(signalAudio, frequenceEchantillonnage, cutoff_frequency=4186, kernel_size=5):
    # Appliquer les filtres
    signal_filtre = filtre_pass_bas(signalAudio, cutoff_frequency, frequenceEchantillonnage)
    signal_filtre = medfilt(signal_filtre, kernel_size=kernel_size)
    return signal_filtre

def estimer_hauteur(signal_filtre, frequence_echantillonnage, longueurFft, longueur_saut, seuil_db):
    # Estimer la hauteur pour chaque trame du signal audio.
    D = librosa.stft(signal_filtre, n_fft=longueurFft, hop_length=longueur_saut)
    magnitude_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    frequences = librosa.fft_frequencies(sr=frequence_echantillonnage, n_fft=longueurFft)

    estimation_pitch = []
    for i in range(magnitude_db.shape[1]):
        peaks, _ = find_peaks(magnitude_db[:, i], height=seuil_db)
        estimation_pitch.append(peaks)

    return estimation_pitch, frequences, magnitude_db

def pitch_vers_note(pitch):
    # Convertir une fréquence en nom de note.
    if pitch <= 0:
        return 'silence'
    note_midi = librosa.hz_to_midi(pitch)
    nom_note = librosa.midi_to_note(note_midi)
    return nom_note.replace('♯', '#').replace('♭', 'b')

def creer_partition(estimation_pitch, frequences, frequence_echantillonnage, longueurFft):
    # Créer une partition musicale à partir des peaks estimées.
    notes_detectees = [[pitch_vers_note(frequences[p]) for p in frame] for frame in estimation_pitch]
    partition_musicale = stream.Score()
    partie_musicale = stream.Part()
    partie_musicale.append(metadata.Metadata(title='Transcription Audio', composer='Transcription Automatique'))

    notes_actuelles = set()
    compteur_notes = {}
    duree_trame = longueurFft * 0.5 / frequence_echantillonnage
    duree_minimale = 0.125

    for i, trame_notes in enumerate(notes_detectees):
        decalage_temps = i * duree_trame

        notes_terminees = notes_actuelles - set(trame_notes)
        for note_terminee in notes_terminees:
            duree_note = compteur_notes.pop(note_terminee, 0) * duree_trame
            if duree_note > 0:
                if note_terminee == 'silence':
                    note_silence = note.Rest(quarterLength=max(duree_note, duree_minimale))
                    partie_musicale.insert(decalage_temps - duree_note, note_silence)
                else:
                    note_musicale = note.Note(note_terminee)
                    note_musicale.quarterLength = max(duree_note, duree_minimale)
                    partie_musicale.insert(decalage_temps - duree_note, note_musicale)

        nouvelles_notes = set(trame_notes) - notes_actuelles
        for nouvelle_note in nouvelles_notes:
            compteur_notes[nouvelle_note] = 0

        for note_active in notes_actuelles.intersection(trame_notes):
            compteur_notes[note_active] += 1

        notes_actuelles = set(trame_notes)

        if not trame_notes:
            note_silence = note.Rest(quarterLength=duree_minimale)
            partie_musicale.insert(decalage_temps, note_silence)

    if len(partie_musicale.notesAndRests) > 0:
        partition_musicale.append(partie_musicale)
        chemin_midi = 'partition0010.mid'
        partition_musicale.write('midi', fp=chemin_midi)
        print(f"Fichier MIDI écrit à {chemin_midi}")
    else:
        print("Erreur : aucune note ou silence trouvé dans la partition.")

def visualiser_spectrogramme(magnitude_db, frequence_echantillonnage, longueur_saut, estimation_pitch, filtered_signal):
    # spectogramme
    plt.figure(figsize=(15, 5))
    librosa.display.specshow(magnitude_db, sr=frequence_echantillonnage, hop_length=longueur_saut, x_axis='time',
                             y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogramme avec Pics Détectés')

    # Tracer les pics détectés
    for i, peaks in enumerate(estimation_pitch):
        for peak in peaks:
            plt.plot(i * longueur_saut / frequence_echantillonnage,
                     librosa.fft_frequencies(sr=frequence_echantillonnage)[peak], 'ro')

    plt.tight_layout()
    plt.show()
    plt.figure(figsize=(15, 5))
    librosa.display.specshow(magnitude_db, sr=frequence_echantillonnage, hop_length=longueur_saut, x_axis='time',
                             y_axis='log')
    # forme d'onde
    plt.figure(figsize=(15, 5))
    librosa.display.waveshow(filtered_signal, sr=frequence_echantillonnage)
    plt.title('Forme d\'onde du signal audio filtré')
    plt.tight_layout()
    plt.show()
    # Le chromagram
    hop_length = 512
    chromagram = librosa.feature.chroma_cqt(y=filtered_signal, sr=frequence_echantillonnage, hop_length=hop_length)


    plt.figure(figsize=(15, 5))
    librosa.display.specshow(chromagram, x_axis='time', y_axis='chroma', hop_length=hop_length, cmap='coolwarm')
    plt.colorbar()
    plt.title('Chromagram')
    plt.tight_layout()
    plt.show()


def main(path_video, seuil_db,path_fichier_audio,):
    # Fonction principale pour exécuter le processus de transcription audio
    extraire_audio(path_video, path_fichier_audio)
    signal_audio, frequence_echantillonnage = charger_fichier_audio(path_fichier_audio)
    tempo = detecter_tempo(signal_audio, frequence_echantillonnage)


    longueur_saut = int(longueurFft * (1 - recouvrement))
    signal_filtre = appliquer_filtres(signal_audio, frequence_echantillonnage)
    estimation_pitch, frequences, magnitude_db = estimer_hauteur(signal_filtre, frequence_echantillonnage, longueurFft, longueur_saut, seuil_db)
    creer_partition(estimation_pitch, frequences, frequence_echantillonnage, longueurFft)
    visualiser_spectrogramme(magnitude_db, frequence_echantillonnage, longueur_saut, estimation_pitch, signal_filtre)
