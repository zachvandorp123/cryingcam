# Use an official lightweight Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg

# Copy only the necessary files
COPY cryingcam.py ./cryingcam.py
COPY baby_cry_detection_model.keras ./baby_cry_detection_model.keras
COPY notifications.py ./notifications.py
COPY light_functions.py ./light_functions.py
COPY requirements.txt /app/


RUN pip install --no-cache-dir -r requirements.txt
# Make port 8123 available to the world outside this container
EXPOSE 8123

# Define environment variable to force Python's stdout and stderr to be unbuffered.
ENV PYTHONUNBUFFERED=1

# Run cryingcam.py when the container launches
CMD ["python", "cryingcam.py"]
