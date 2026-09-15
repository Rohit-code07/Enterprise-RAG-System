# Use Python 3.11 slim to ensure maximum compatibility with ML libraries (ChromaDB, PyTorch, SentenceTransformers)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/user/.local/bin:$PATH" \
    PORT=7860

# Hugging Face Spaces requires running as a non-root user with ID 1000
RUN useradd -m -u 1000 user

# Set the working directory
WORKDIR /home/user/app

# Install system dependencies required for building ML wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Change ownership of the app directory to the new user
RUN chown -R user:user /home/user/app

# Switch to the non-root user
USER user

# Copy requirements first to leverage Docker layer caching
COPY --chown=user:user requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY --chown=user:user . .

# Expose the port used by Hugging Face Spaces
EXPOSE 7860

# Start the FastAPI application using Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860"]
