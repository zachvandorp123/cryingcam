import os
import librosa
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.callbacks import TensorBoard
import keras
import time

def load_data(file_path):
    print(f"Loading data from {file_path}...")
    try:
        X, sample_rate = librosa.load(file_path, sr=44100)
        mfccs = librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40)
        mfccs_scaled_features = np.mean(mfccs.T, axis=0)
    except Exception as e:
        print("Error encountered while parsing file:", file_path)
        print(str(e))
        return None
    return mfccs_scaled_features


# Prepare the model
model = Sequential(
    [
        Dense(256, input_shape=(40,)),
        Activation("relu"),
        Dropout(0.5),
        Dense(256),
        Activation("relu"),
        Dropout(0.5),
        Dense(1),
        Activation("sigmoid"),
    ]
)
model.compile(loss="binary_crossentropy", optimizer="Adam", metrics=["accuracy"])

features = []
for folder_label in [
    ("training_audio/baby_crying", 1),
    ("training_audio/not_crying", 0),
]:
    folder, label = folder_label
    for file_name in os.listdir(folder):
        if file_name.endswith(".mp4"):  # Ensure processing only video files
            print(f"Processing {file_name} in {folder}...")
            video_path = os.path.join(folder, file_name)
            audio_directory = os.path.join(folder, "processed_audio")
            os.makedirs(audio_directory, exist_ok=True)

            # Process each generated audio segment
            for audio_file in os.listdir(audio_directory):
                if audio_file.endswith(".wav"):
                    audio_path = os.path.join(audio_directory, audio_file)
                    data = load_data(audio_path)
                    if data is not None:
                        features.append([data, label])

if not features:
    raise ValueError(
        "No valid audio files processed. Check the paths and file formats."
    )

# Prepare data for training
features_df = np.array(features, dtype=object)
X = np.array(features_df[:, 0].tolist())
y = np.array(features_df[:, 1].tolist())
labelencoder = LabelEncoder()
y = labelencoder.fit_transform(y)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Train the model
timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
tensorboard_callback = TensorBoard(log_dir=f"logs/{timestamp}", histogram_freq=1)
model.fit(
    X_train,
    y_train,
    epochs=50,
    batch_size=32,
    validation_data=(X_test, y_test),
    callbacks=[tensorboard_callback],
)

# Save the model
keras.saving.save_model(model, "baby_cry_detection_model.keras")
print("Model training complete and saved.")
