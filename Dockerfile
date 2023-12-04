# # Use the official Python image as the base image
# FROM python:3.8

# # Set the working directory in the container
# WORKDIR /app

# # Copy the application files into the working directory
# COPY . /app

# # Install the application dependencies
# RUN pip install -r requirements.txt

# # Define the entry point for the container
# # CMD ["flask", "run", "--host=127.0.0.1:5000"]
# RUN python .\app.py

# EXPOSE 5000

# DockerfileCopy code# Base image
FROM python:3.9-slim

# Working directory
WORKDIR /app
# COPY . /app

# Copy requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Expose the server port
EXPOSE 8080

# Command to start the server
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
# CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]