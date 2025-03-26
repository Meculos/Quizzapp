# Use official Python image as a base
FROM python:3.12.5

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt  

# Copy the entire project (AFTER installing dependencies)
COPY . .  

# Collect static files (AFTER project files are copied)
RUN python manage.py collectstatic --noinput  

# Expose port 8000
EXPOSE 8000

# Run Django ASGI server with Daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "quiz_project.asgi:application"]
