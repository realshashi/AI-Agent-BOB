FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY vercel_requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r vercel_requirements.txt

# Copy the application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main.py
ENV FLASK_DEBUG=0

# Expose the port
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]