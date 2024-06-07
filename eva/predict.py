import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import tensorflow as tf
import librosa
import keyboard
import pyaudio
import wave
import simpleaudio as sa

def preprocess_audio(file_path, n_mels=128, n_fft=2048, hop_length=512):
    y, sr = librosa.load(file_path, sr=None)
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, n_fft=n_fft, hop_length=hop_length)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    return mel_spec_db

def predict_command(file_path, model, commands):
    mel_spec_db = preprocess_audio(file_path)
    mel_spec_db = mel_spec_db[np.newaxis, ..., np.newaxis]  # Add batch and channel dimensions
    prediction = model.predict(mel_spec_db)[0]  # Remove batch dimension
    certainties = {command: prediction[i] for i, command in enumerate(commands)}
    predicted_label = np.argmax(prediction)
    predicted_command = commands[predicted_label]
    return predicted_command, certainties


def record_audio(output_file, duration=5):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100
    seconds = duration
    filename = output_file

    p = pyaudio.PyAudio()

    print("Recording...")
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []

    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    print("Length of recorded frames:", len(frames))

    stream.stop_stream()
    stream.close()
    p.terminate()

    print("Finished recording.")

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

# playback audio function
def play_audio(file_path):
    wave_obj = sa.WaveObject.from_wave_file(file_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

model = tf.keras.models.load_model('voice_command_model_v2.h5')
# model = tf.keras.models.load_model('voice_command_model_v2.h5')
# model = tf.keras.models.load_model('voice_command_model_v2_novo.h5') # u petek ta



commands = ["next_song", "pause", "volume_down", "volume_up"]

def start_recording():
    output_file = "recorded_audio.wav"
    print("Press the spacebar to start recording...")

    while True:
        keyboard.wait('space')
        record_audio(output_file, duration=2)
        play_audio(output_file)
        predicted_command = predict_command(output_file, model, commands)
        print(f"Predicted Command: {predicted_command}")

start_recording()


#dober dan jasa tu je zeljena funkccija
def predict_from_wav(file_path, model, commands): #zeli met wav, list of commands in model
    # tu mas commands = ["next_song", "pause", "volume_down", "volume_up"]
    predicted_command, certainties = predict_command(file_path, model, commands)
    return predicted_command
