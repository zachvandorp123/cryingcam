import os
import subprocess
import pyaudio
import numpy as np
import librosa
import wave
import time
from tensorflow.keras.models import load_model
from shutil import move  # Import move to handle file moving
from notifications import send_notification

# Configuration for the audio stream
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024  # Number of frames read at once
last_notification_time = 0
cooldown_seconds = 30  # Cooldown period in seconds


def predict_cry(model, features):
    features = np.expand_dims(features, axis=0)
    prediction = model.predict(features)
    is_crying = prediction[0][0] >= 0.5
    print(f"Prediction confidence: {prediction[0][0]}")
    return is_crying


def extract_features_from_file(file_path):
    try:
        X, sample_rate = librosa.load(file_path, sr=44100)
        mfccs = librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40)
        return np.mean(mfccs.T, axis=0)
    except Exception as e:
        print(f"Error encountered while processing file: {file_path}")
        print(str(e))
        return None


def save_audio_clip(data, folder="temp"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(folder, f"clip_{timestamp}.wav")
    wf = wave.open(filename, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()
    return filename


def stream_and_detect(rtsp_url, model, listen=False):
    command = [
        "ffmpeg",
        "-i",
        rtsp_url,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        str(RATE),
        "-ac",
        str(CHANNELS),
        "-f",
        "s16le",
        "-",
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        output=True,
        frames_per_buffer=CHUNK,
    )
    audio_buffer = bytes()
    global last_notification_time

    try:
        while True:
            data = process.stdout.read(CHUNK * CHANNELS * 2)
            if not data:
                break

            audio_buffer += data
            if listen:
                stream.write(data)

            if len(audio_buffer) >= RATE * 2 * 5:  # 5 seconds of audio
                current_data = audio_buffer[: RATE * 2 * 5]
                audio_buffer = audio_buffer[RATE * 2 * 5 :]
                audio_file = save_audio_clip(current_data)
                features = extract_features_from_file(audio_file)
                if features is not None:
                    is_crying = predict_cry(model, features)
                    current_time = time.time()
                    if is_crying:
                        print("Crying detected!")
                        if current_time - last_notification_time > cooldown_seconds:
                            send_notification(
                                "Alert: Baby is crying!", "Home Assistant Notification"
                            )
                            last_notification_time = current_time
                        if not os.path.exists("detected_crying"):
                            os.makedirs("detected_crying")
                        move(
                            audio_file,
                            os.path.join(
                                "detected_crying", os.path.basename(audio_file)
                            ),
                        )
                    else:
                        os.remove(audio_file)
                        print("No crying detected, file deleted.")
                else:
                    os.remove(audio_file)  # Clean up if features could not be extracted
                    print("Not enough data for prediction, file deleted.")
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        process.terminate()


# Main execution
if __name__ == "__main__":
    model = load_model("baby_cry_detection_model.keras")
    rtsp_url = f"rtsp://{os.getenv('WEBCAM_USERNAME')}:{os.getenv('WEBCAM_PW')}@{os.getenv('WEBCAM_IP_ADDRESS')}:{os.getenv('WEBCAM_PORT')}/h264Preview_02_sub"
    stream_and_detect(rtsp_url, model, listen=False)
