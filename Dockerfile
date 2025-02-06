# Use the official Python image from the Docker Hub
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Copy dependency definitions to the container
COPY pyproject.toml poetry.lock README.md ./

# Install dependencies using Poetry
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy project files to the container
COPY src/ .

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
