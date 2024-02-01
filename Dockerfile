# Use an official Python runtime as a parent image
FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app/
COPY . /app/

# Expose the port on which the app will run
EXPOSE 8000

# Command to run on container start
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "credit_approval_system.wsgi:application"]
