# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make port 8123 available to the world outside this container
EXPOSE 8123

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run cryingcam.py when the container launches
CMD ["python", "cryingcam.py"]
