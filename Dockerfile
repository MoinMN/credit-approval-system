# Use an official Python runtime as a parent image
FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=myproject.settings

# Install the PostgreSQL client
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Create and set the working directory
RUN mkdir /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port that Django will run on
EXPOSE 8000

# CMD to start the Django development server
CMD ["python", "manage.py", "runserver"]

