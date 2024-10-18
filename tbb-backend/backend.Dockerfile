# Use an official Python 3.12 slim image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /backend-app

# # Install build tools and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, wheel, and setuptools
RUN pip install --upgrade pip wheel setuptools

# Copy the current directory contents into the container at /backend-app
COPY . /backend-app

# Install specific versions of dependencies
RUN pip install -r requirements.txt

# Expose port 8000 to allow access to your application
EXPOSE 8000

# Command to run the application
# CMD ["python", "run.py"]
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]
