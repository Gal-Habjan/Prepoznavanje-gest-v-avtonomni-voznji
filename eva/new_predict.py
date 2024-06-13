import numpy as np
import tensorflow as tf
import librosa

# Preprocess audio data
def preprocess_audio(y, sr, n_mels=128, n_fft=2048, hop_length=512):
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, n_fft=n_fft, hop_length=hop_length)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    return mel_spec_db

def predict(y, sr, model, commands):
    mel_spec_db = preprocess_audio(y, sr)
    mel_spec_db = mel_spec_db[np.newaxis, ..., np.newaxis]  # Add batch and channel dimensions
    prediction = model.predict(mel_spec_db)[0]  # Remove batch dimension
    certainties = {command: prediction[i] for i, command in enumerate(commands)}
    predicted_label = np.argmax(prediction)
    predicted_command = commands[predicted_label]
    return predicted_command, certainties


model = tf.keras.models.load_model('voice_command_model_v2.h5')
commands = ["next_song", "pause", "volume_down", "volume_up"]

'''
Tu dobis y = audio data, sr je sample rate, ce lahko to nardis u tvoji kodi lahka sam to dvoje passas
'''
#file = 'waw.wav'
#y, sr = librosa.load(file, sr=None)

#predicted_command, certainties = predict(y, sr, model, commands)
# print(f"Predicted Command: {predicted_command}")
# print(f"Certainties: {certainties}")
