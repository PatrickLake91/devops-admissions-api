FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Ensure Python prints straight to console and the application package is on the path
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Flask configuration
ENV FLASK_APP=app:create_app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Expose the port that Flask will run on
EXPOSE 5000

# Default command to run the Flask app
CMD ["flask", "run"]
