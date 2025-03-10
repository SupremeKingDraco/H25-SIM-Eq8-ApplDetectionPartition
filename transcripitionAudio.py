import numpy as np
import librosa, librosa.display

import matplotlib.pyplot as plt

import os
from music21.tempo import MetronomeMark
from music21 import *
import moviepy.editor as mp

nomVideo = mp.VideoFileClip(r"C:\Users\TheBr\Downloads\Yiruma_-_River_Flows_In_You_Intermediate_Piano_Tutorial.mp4")
nomVideo.audio.write_audiofile(r"C:\Users\TheBr\Downloads\versionAudio.mp3")
path = r"C:\Users\TheBr\Downloads"
filename = os.path.join(path, "versionAudio.mp3")


sr = 44100                               # fréquence d'échantillionnage
nfft = 2048                              # longueur de la fenêtre FFT
overlap = 0.5                            # Pourcentage de chevauchement du saut
hop_length = int(nfft*(1-overlap))       # nombre d'échantillons entre les frames successives
n_bins = 72                              # nombre de bandes de fréquence
mag_exp = 4                              # Exposant de la magnitude
seuil_dB = -61




#Vérfier si le fichier existe
if not os.path.exists(filename):
    print(f"Error: File '{filename}' does not exist.")
else:
    print(f"File '{filename}' found. Proceeding to load...")
    y, sr = librosa.load(filename)


#Trouver le bpm de la pièce
tempo, beats_frames = librosa.beat.beat_track(y=y, sr=sr)

#Transformer le numpy array tempo en integer

tempo = tempo.item()

#Formatter le tempo
tempo = int(2 * round(tempo / 2))
#Créer un objet pour représenter le tempo dans music21
mm = MetronomeMark(referent='quarter', number=tempo)

# Matrice qui contient tout les calculs FFT selon la durée fenêtre STFT
D = librosa.stft(y, n_fft=nfft, hop_length=hop_length)
#Trouver l'amplitude et le convertir en décibels
magnitude_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
#Déterminer les fréquences des calculs dans la matrice D
frequences = librosa.fft_frequencies(sr=sr, n_fft=nfft)


estimer_pitch = []

for i in range(magnitude_db.shape[1]):
    max_db = np.max(magnitude_db[:, i])
    if max_db > seuil_dB: #Trouver la note la plus forte dans la frame
        max_freq_idx = np.argmax(magnitude_db[:, i])
        freq = frequences[max_freq_idx]
        estimer_pitch.append(freq)
    else:
        estimer_pitch.append(0)  # Silence or noise

# Convert frequencies to note names
def pitch_a_note(pitch):
    if pitch <= 0:
        return 'rest'
    #Créer un midi à l'aide des fréquences
    midi_note = librosa.hz_to_midi(pitch)
    #Prendre le nom de la note du midi
    note_nom = librosa.midi_to_note(midi_note)
    return note_nom.replace('♯', '#').replace('♭', 'b')


#Créer un tableau de notes en utilisant la fonction pitch_to_note pour chaque élément de estimer_pitch
notes = [pitch_a_note(p) for p in estimer_pitch]
notes = [n for n in notes if n != 'rest']  # Enlever les silences

#Créer un score et un part
score = stream.Score()
part = stream.Part()
score.metadata = metadata.Metadata(title='Audio Transcrie', composer='Transcription automatique')
part.append(mm)


duree_quarter = 60 / tempo
duree_frame = hop_length / sr
frames_par_quarter = duree_quarter / duree_frame

note_presente = None
compteur = 0
min_duration = 0.125  # Durée minimum d'une note

#Entrer les notes dans la partition avec leurs durées
for n in notes:
    if n != note_presente:
        if note_presente is not None:
            # Calculer durée passer en quarter notes
            duree_passee = compteur / frames_par_quarter


            formatter_duree = round(duree_passee * 4) / 4

            # Assurer la duree minimum
            duree = max(formatter_duree, min_duration)

            # Créer note
            music_note = note.Note(note_presente)
            music_note.quarterLength = duree
            part.append(music_note)


        note_presente = n
        compteur = 1
    else:
        compteur += 1
    #Pour la dernière note
    if i == len(notes) - 1 and note_presente is not None:
        duree_passee = compteur / frames_par_quarter
        formatter_duree = round(duree_passee * 4) / 4
        duree = max(formatter_duree, min_duration)

        music_note = note.Note(note_presente)
        music_note.quarterLength = duree
        part.append(music_note)


# Quantifier le part à le grid de la 16ième note
part.quantize([8], inPlace=True)

score.append(part)
score.show()
score.write('midi', fp='score0001.mid')


