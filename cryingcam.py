import os
import subprocess
import numpy as np
import librosa
from tensorflow.keras.models import load_model
from shutil import move
from notifications import send_notification
from light_functions import baby_crying_light_routine
import time
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import threading

load_dotenv("stack.env")

app = Flask(__name__)
is_paused = False


@app.route("/command", methods=["POST"])
def command():
    global is_paused
    data = request.get_json()
    if data is not None and "pause" in data:
        pause_value = data["pause"].lower() == "true"  # Convert the string to boolean
        is_paused = pause_value
        status = "paused" if is_paused else "resumed"
        return jsonify({"status": "success", "action": status}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid request"}), 400


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"paused": is_paused}), 200


def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

# Configuration for the audio processing
CHANNELS = 1
RATE = 44100
last_notification_time = 0
cooldown_seconds = 30  # Cooldown period in seconds
cry_detections = []  # Track recent times of crying detections
notification_threshold = 30  # Minimum time in seconds of consistent crying to notify
save_crying = False  # Option to not save crying clips by default
save_non_crying = False  # Option to save non-crying clips for review

temp_directory = "temp"
os.makedirs(temp_directory, exist_ok=True)

def predict_cry(model, features):
    features = np.expand_dims(features, axis=0)
    prediction = model.predict(features)
    is_crying = prediction[0][0] >= 0.5
    print(f"Prediction confidence: {prediction[0][0]}")
    return is_crying


def extract_features_from_file(file_path):
    try:
        X, sample_rate = librosa.load(file_path, sr=RATE)
        mfccs = librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40)
        return np.mean(mfccs.T, axis=0)
    except Exception as e:
        print(f"Error encountered while processing file: {file_path}")
        print(str(e))
        return None

def save_rtsp_to_wav(rtsp_url, duration, output_filename):
    command = [
        "ffmpeg",
        "-rtsp_transport", 
        "tcp",
        "-i",
        rtsp_url,
        "-t",
        str(duration),
        "-acodec",
        "pcm_s16le",
        "-ar",
        "44100",
        "-ac",
        "1",
        "-y",
        output_filename,
    ]
    print('attempting save rtsp to wave command')
    subprocess.run(
        command,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=20,
    )
    print(f"Saved audio to {output_filename}")
    return output_filename

def handle_cry_detection(output_filename, model):
    features = extract_features_from_file(output_filename)
    global last_notification_time
    global cry_detections
    if features is not None:
        is_crying = predict_cry(model, features)
        current_time = time.time()
        if is_crying:
            cry_detections.append(current_time)
            # Remove old detections
            cry_detections = [
                t for t in cry_detections if current_time - t < notification_threshold
            ]
            print(f"Crying detected. Total detections in window: {len(cry_detections)}")
            if (
                len(cry_detections) >= 3
            ):  # At least 3 detections within the notification threshold
                print(
                    "Crying detected multiple times within the notification threshold!"
                )
                if current_time - last_notification_time > cooldown_seconds:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    message = (
                        f"Alert: Baby is crying! Detected consistently at {timestamp}"
                    )
                    send_notification(message, "Home Assistant Notification")
                    baby_crying_light_routine()
                    last_notification_time = current_time
                if save_crying:
                    if not os.path.exists("detected_crying"):
                        os.makedirs("detected_crying")
                    move(
                        output_filename,
                        os.path.join(
                            "detected_crying", os.path.basename(output_filename)
                        ),
                    )
                else:
                    os.remove(output_filename)
                    print("Crying detected, file not saved as per settings.")
            else:
                os.remove(output_filename)
                print("Crying detected, awaiting more confirmation.")
        else:
            if save_non_crying:
                if not os.path.exists("not_crying"):
                    os.makedirs("not_crying")
                move(
                    output_filename,
                    os.path.join("not_crying", os.path.basename(output_filename)),
                )
                print("No crying detected, file saved for review.")
            else:
                os.remove(output_filename)
                print("No crying detected, file deleted.")
    else:
        os.remove(output_filename)
        print("Not enough data for prediction, file deleted.")

# Main execution
if __name__ == "__main__":
    model = load_model("baby_cry_detection_model.keras")
    print('model_loaded')
    rtsp_url = f"rtsp://{os.getenv('WEBCAM_USERNAME')}:{os.getenv('WEBCAM_PW')}@{os.getenv('WEBCAM_IP_ADDRESS')}:{os.getenv('WEBCAM_PORT')}/h264Preview_02_sub"
    while True:
        if not is_paused:
            output_filename = save_rtsp_to_wav(
                rtsp_url, 5, f"temp/clip_{time.strftime('%Y%m%d_%H%M%S')}.wav"
            )
            handle_cry_detection(output_filename, model)