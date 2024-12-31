# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ .

# Expose the port the application will run on
EXPOSE 5002

# Set the environment variable for Flask
ENV FLASK_APP=app.py

# Run the application
CMD ["python", "app.py"]
