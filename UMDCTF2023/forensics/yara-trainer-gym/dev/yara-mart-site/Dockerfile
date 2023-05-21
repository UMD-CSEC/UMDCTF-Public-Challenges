# Set base image
FROM python:3.11-slim-buster

# Install dependencies
RUN apt-get update && apt-get install -y libyara-dev yara gcc
# Set working directory
WORKDIR /app

# Copy the Flask app files to the container
COPY yara_mart_site /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 for the Flask app to listen on
EXPOSE 5000

# Start the Flask app
CMD ["python", "app.py"]
