# Use Python 3.10 slim base image
FROM python:3.11.0-slim

# Set the root working directory inside the container
WORKDIR /app

# Copy requirements file and install Python dependencies
COPY reqt.txt .
RUN pip install --no-cache-dir -r reqt.txt

# Copy the entire project into the container
COPY . .

# Optional: Add a non-root user for security
RUN adduser --disabled-password --gecos "" myuser && \
    chown -R myuser:myuser /app
USER myuser

# Set environment variables
ENV PATH="/home/myuser/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Expose port 8000 used by ADK
EXPOSE 8000

# Set the working directory to where adk web should run from
WORKDIR /app/auto

# Start the ADK agent and bind to all interfaces so Docker can expose it
CMD ["adk", "web", "--host", "0.0.0.0", "--port", "8000"]
