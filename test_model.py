import os
import numpy as np
import librosa
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix, classification_report


def extract_features(audio_file):
    try:
        X, sample_rate = librosa.load(audio_file, sr=44100)
        mfccs = librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40)
        mfccs_scaled_features = np.mean(mfccs.T, axis=0)
    except Exception as e:
        print(f"Error encountered while parsing file: {audio_file}")
        print(str(e))
        return None
    return mfccs_scaled_features


def predict_cry(model, features):
    features = np.expand_dims(features, axis=0)  # Reshape for prediction
    prediction = model.predict(features)
    return prediction[0][0]


# Load the model
model = load_model("baby_cry_detection_model.keras")

# Directories for crying and not crying holdouts
directories = {
    "training_audio/baby_crying/processed_audio": 1,  # Label '1' for crying
    "training_audio/not_crying/processed_audio": 0,  # Label '0' for not crying
}

labels = []  # True labels
predictions = []  # Model predictions
false_positives = []  # List to store details of false positives

# Process each directory and its files
for directory, label in directories.items():
    for filename in os.listdir(directory):
        if filename.endswith(".wav"):
            audio_path = os.path.join(directory, filename)
            features = extract_features(audio_path)
            if features is not None:
                confidence = predict_cry(model, features)
                predicted_label = 1 if confidence >= 0.9 else 0
                if predicted_label != label and predicted_label == 1:
                    false_positives.append(
                        (filename, confidence)
                    )  # Add to false positives if wrongly predicted as crying
                print(
                    f"Filename: {filename}, Actual Label: {label}, Predicted Label: {predicted_label}, Confidence: {confidence:.2f}"
                )
                labels.append(label)
                predictions.append(predicted_label)

cm = confusion_matrix(labels, predictions)
print("Confusion Matrix:")
print(cm)
print("\nClassification Report:")
print(classification_report(labels, predictions, target_names=["Not Crying", "Crying"]))

# Print out details of false positives
if false_positives:
    print("\nFalse Positives:")
    for fp in false_positives:
        print(f"Filename: {fp[0]}, Confidence: {fp[1]:.2f}")
else:
    print("\nNo false positives detected.")
