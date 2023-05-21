# Set base image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Add new user
RUN adduser -D -s /bin/sh ctf
RUN chmod -w /home/ctf

# Remove write permissions on directories
RUN chmod a-w /home/ctf
RUN chmod a-w /tmp

# Copy the requirements file to the working directory
COPY requirements.txt .

# Make directory for templates
RUN mkdir templates

# Copy flag file in
COPY flag.txt .

# Modify flag permissions to give read-only permissions
RUN chmod a-w flag.txt
RUN chmod a-x flag.txt
RUN chmod a+r flag.txt

# Copy the templates to the working directory
COPY templates/ templates/.

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app to the working directory
COPY app.py .

# Switch into ctf user
USER ctf

# Expose port 5000 for the Flask app
EXPOSE 5000

# Set the command to start the Flask app
CMD ["python", "app.py"]