# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /code

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy only the pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock /code/

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy the Django project code
COPY . /code/

# Expose the port the app runs on
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
