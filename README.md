# Baby Cry Detection System

## Description
This project is a baby monitoring system designed to detect crying sounds using audio surveillance technology. It utilizes advanced machine learning algorithms to analyze audio data in real-time, aiming to provide parents or caregivers immediate notifications when a baby cries.

## Features
- **Real-time Audio Processing**: Analyzes audio streams to detect baby crying sounds.
- **Notification System**: Integrates with Home Assistant to send real-time notifications to a user's mobile device when crying is detected.
- **Docker Support**: Containerized for easy deployment and scalability.

## Technologies Used
- **Python**: Primary programming language used for scripting and machine learning logic.
- **Librosa**: For audio signal processing.
- **TensorFlow/Keras**: Utilized for building and training the machine learning model.
- **Docker**: For containerizing the application, ensuring consistency across different environments.
- **Home Assistant**: For setting up automation and notification systems within a smart home environment.

## Installation
Clone the repository and navigate to the directory:
```bash
git clone https://github.com/yourusername/babycry-detector.git
cd babycry-detector


##Usage
Once the container is running, it will continuously analyze audio data from the specified source and send notifications if crying is detected.

##Training Data Management
To add new training data:
Crying Sounds: Add .wav files of baby crying sounds to training_audio/baby_crying.
Non-crying Sounds: Add .wav files of normal or non-crying baby sounds to training_audio/not_crying.
##Enhancing Model Accuracy
After the system has saved a collection of detected crying clips in the detected_crying folder, you can review these clips to confirm their accuracy. Validated clips can then be moved back into the training_audio/baby_crying folder to retrain the model, thereby enhancing its accuracy over time.
