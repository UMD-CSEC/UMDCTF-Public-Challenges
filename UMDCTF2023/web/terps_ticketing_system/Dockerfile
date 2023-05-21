# Set base image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Make directory for templates
RUN mkdir templates

# Copy the templates to the working directory
COPY templates/ templates/.

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app to the working directory
COPY app.py .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Set the command to start the Flask app
CMD ["python", "app.py"]