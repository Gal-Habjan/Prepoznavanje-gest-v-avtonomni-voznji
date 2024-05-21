import sounddevice as sd
from scipy.io.wavfile import write
import os

# ekstrakcija audio samples
# def record_audio(filename, duration=2, fs=44100):
#     print("Recording...")
#     recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
#     sd.wait()  # Wait until recording is finished
#     write(filename, fs, recording)
#     print(f"Recording saved as {filename}")
#
# commands = ["next_song", "volume_up", "volume_down", "pause"]
# for command in commands:
#     os.makedirs(command, exist_ok=True)
#     for i in range(1, 31):
#         filename = os.path.join(command, f"{command}_{i}.wav")
#         record_audio(filename)
import sounddevice as sd
from scipy.io.wavfile import write
import os


import librosa
import numpy as np
import os

def preprocess_audio(file_path, n_mels=128, n_fft=2048, hop_length=512):
    y, sr = librosa.load(file_path, sr=None)
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, n_fft=n_fft, hop_length=hop_length)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    return mel_spec_db

def create_dataset(data_dir, output_file):
    labels = []
    features = []
    commands = sorted(os.listdir(data_dir))  # Ensure consistent label ordering
    print("commands", commands)
    for label, command in enumerate(commands):
        command_dir = os.path.join(data_dir, command)
        for file in os.listdir(command_dir):
            file_path = os.path.join(command_dir, file)
            mel_spec_db = preprocess_audio(file_path)
            features.append(mel_spec_db)
            labels.append(label)
    np.savez(output_file, features=np.array(features), labels=np.array(labels))

data_dir = 'dataset'
output_file = 'voice_commands_dataset.npz'
create_dataset(data_dir, output_file)

import numpy as np

# Load the dataset
data = np.load('voice_commands_dataset.npz')

# Extract features and labels
X = data['features']
y = data['labels']

print(f"Features shape: {X.shape}")
print(f"Labels shape: {y.shape}")

# Inspect a single sample
print(f"First feature shape: {X[0].shape}")
print(f"First label: {y[0]}")

import numpy as np
from sklearn.model_selection import train_test_split

# Load the dataset
data = np.load('voice_commands_dataset.npz')
X = data['features']
y = data['labels']

# Reshape X to have an additional dimension for the channel
X = X[..., np.newaxis]

# Train-test split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training samples: {X_train.shape[0]}, Validation samples: {X_val.shape[0]}")

import tensorflow as tf

# Build the model
from tensorflow.keras import layers, models

# Build the model
model = models.Sequential([
    layers.Input(shape=(X_train.shape[1], X_train.shape[2], 1)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(128, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(256, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(4, activation='softmax')
])


model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, epochs=30, validation_data=(X_val, y_val))

# Save the model
model.save('voice_command_model.h5')


# Evaluate the model
loss, accuracy = model.evaluate(X_val, y_val)
print(f"Validation Loss: {loss}")
print(f"Validation Accuracy: {accuracy}")
