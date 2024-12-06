FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /workspace/project2_commerce

# Install system dependencies
RUN apt-get update && apt-get install -y \
    zsh \
    && apt-get clean

# Copy the project files
COPY . /workspace/project2_commerce/

# Install Python dependencies
COPY requirements.txt /workspace/project2_commerce/
RUN pip install --upgrade pip
RUN pip install -r /workspace/project2_commerce/requirements.txt

# Set the default shell to zsh
SHELL ["/bin/zsh", "-c"]

# Expose the port the app runs on
EXPOSE 8000

# Run migrations and then the Django development server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:${PORT:-8000}"]