# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Create a volume for the database (DB) and logs
VOLUME /app


# Define the command to run your application
CMD ["python", "manager.py"]
