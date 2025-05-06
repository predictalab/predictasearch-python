# Use a lightweight base image
FROM python:3.11-slim

# Set API key environment variable
ENV PREDICTA_API_KEY=iamsupposedtobeavalidpredictaapikey

# Set working directory
WORKDIR /app

# Copy files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip \
    && pip install . \
    && apt-get clean

# Default command
ENTRYPOINT ["predictasearch"]
