import os
import numpy as np
import librosa
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras import layers, models, optimizers


def extract_features(audio_file, sr=22050, duration=3):
    y, _ = librosa.load(audio_file, sr=sr, duration=duration)
    features = librosa.feature.mfcc(y=y, sr=sr)
    return features

def load_data(dataset_folder):
    X = []
    y = []
    print("Loading data from dataset folder:", dataset_folder)
    for command_folder in os.listdir(dataset_folder):
        command_folder_path = os.path.join(dataset_folder, command_folder)
        if os.path.isdir(command_folder_path):
            print("Processing command folder:", command_folder)
            for file_name in os.listdir(command_folder_path):
                if file_name.endswith(".wav"):
                    audio_file = os.path.join(command_folder_path, file_name)
                    command_label = command_folder.replace("_", " ")
                    print("Final command label for file:", command_label)
                    features = extract_features(audio_file)
                    X.append(features)
                    y.append(command_label)
                    print("Features extracted and appended to X, label appended to y")
    return X, y

dataset_folder = "dataset"
X, y = load_data(dataset_folder)

X = np.array(X)
y = np.array(y)

X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.2, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

label_encoder = LabelEncoder()
y_train_encoded = label_encoder.fit_transform(y_train)
y_val_encoded = label_encoder.transform(y_val)
y_test_encoded = label_encoder.transform(y_test)
print("y_train shape:", y_train_encoded.shape)
print("y_val shape:", y_val_encoded.shape)
print("y_test shape:", y_test_encoded.shape)


num_features = 20 #mfcc shape
num_frames = 300 #clip length
num_classes = 4  #num of commands
X_train_reshaped = X_train.reshape((X_train.shape[0], -1))
X_val_reshaped = X_val.reshape((X_val.shape[0], -1))
X_test_reshaped = X_test.reshape((X_test.shape[0], -1))

model = models.Sequential([
    layers.Input(shape=(num_features, num_frames)),  # Define input shape based on the extracted features
    layers.Flatten(),  # Flatten the input
    layers.Dense(128, activation='relu'),  # Add a dense layer with ReLU activation
    layers.Dense(num_classes, activation='softmax')  # Add an output layer with softmax activation
])

optimizer = optimizers.Adam(learning_rate=0.001)
model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

patience = 3
min_delta = 0.001
best_val_loss = np.inf

for epoch in range(20):
    history = model.fit(X_train, y_train_encoded, epochs=1, validation_data=(X_val, y_val_encoded))

    val_loss = history.history['val_loss'][0]
    if val_loss < best_val_loss - min_delta:
        best_val_loss = val_loss
        patience_counter = 0
    else:
        patience_counter += 1

    if patience_counter >= patience:
        print(f"Early stopping after epoch {epoch + 1} as validation loss did not improve.")
        break

test_loss, test_accuracy = model.evaluate(X_test, y_test_encoded)
print("Test Loss:", test_loss)
print("Test Accuracy:", test_accuracy)
