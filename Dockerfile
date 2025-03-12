# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Copy dependency definitions to the container
COPY pyproject.toml poetry.lock README.md gunicorn_config.py ./

RUN apt-get update && apt-get install -y locales && \
    sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen ru_RU.UTF-8

ENV LANG ru_RU.UTF-8
ENV LANGUAGE ru_RU:ru
ENV LC_ALL ru_RU.UTF-8

# Install dependencies using Poetry
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy project files to the container
COPY src/ .

# Expose port 8000
EXPOSE 8000

# Run the application with Gunicorn
CMD ["gunicorn", "--config", "gunicorn_config.py", "config.wsgi:application"]
