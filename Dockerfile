# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tesseract-ocr \
    tesseract-ocr-spa \
    ffmpeg \
    libsm6 \
    libxext6 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install UV (fast Python package installer, drop-in replacement for pip)
ENV UV_COMPILE_BYTECODE=0
ENV UV_LINK_MODE=copy
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set the working directory in the container
WORKDIR /app

# Copy and install Python dependencies with UV (much faster than pip)
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Download spaCy model
RUN python -m spacy download es_core_news_sm

# Copy the rest of the application code into the container at /app
COPY . .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run streamlit when the container launches
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
