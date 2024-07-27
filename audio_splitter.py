import os
import subprocess


def extract_and_split_audio(video_file, output_directory):
    print(f"Extracting audio from {video_file}...")
    audio_file = os.path.join(
        output_directory, os.path.basename(video_file).replace(".mp4", ".wav")
    )
    # Extract audio with specified bitrate
    command = [
        "ffmpeg",
        "-y",  # Overwrite existing files without asking
        "-i",
        video_file,
        "-vn",  # No video
        "-acodec",
        "pcm_s16le",  # Linear PCM format
        "-ar",
        "44100",  # Audio sample rate
        "-ac",
        "1",  # Mono channel
        "-ab",
        "700k",  # Set bitrate to 700 kbits per second
        audio_file,
    ]
    subprocess.run(command, check=True)

    # Split the audio file into 5-second clips, maintaining the same bitrate
    split_command = [
        "ffmpeg",
        "-y",  # Overwrite existing files without asking
        "-i",
        audio_file,
        "-f",
        "segment",
        "-segment_time",
        "5",  # 5 seconds per segment
        "-c",
        "copy",  # Copy the audio without re-encoding
        os.path.join(
            output_directory, os.path.basename(audio_file).replace(".wav", "_%03d.wav")
        ),
    ]
    subprocess.run(split_command, check=True)

    # Delete the original long audio file to avoid using it in training
    os.remove(audio_file)  # Be careful with this line; it deletes the file permanently

for folder_label in [
    ("training_audio/baby_crying", "crying"),
    ("training_audio/not_crying", "not_crying"),
]:
    folder, label = folder_label
    for file_name in os.listdir(folder):
        if file_name.endswith(".mp4"):  # Ensure processing only video files
            print(f"Processing {file_name} in {folder}...")
            video_path = os.path.join(folder, file_name)
            audio_directory = os.path.join(folder, "processed_audio")
            os.makedirs(audio_directory, exist_ok=True)

            extract_and_split_audio(video_path, audio_directory)
