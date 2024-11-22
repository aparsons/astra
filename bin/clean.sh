#! /bin/bash

rm -f db.sqlite3

# Function to delete all Django migrations in the specified directory
delete_migrations() {
    local MIGRATIONS_DIR=$1

    # Check if the directory exists
    if [ ! -d "$MIGRATIONS_DIR" ]; then
        echo "Directory $MIGRATIONS_DIR does not exist."
        return 1
    fi

    # Find and delete all migration files except __init__.py
    find "$MIGRATIONS_DIR" -type f -name "*.py" ! -name "__init__.py" -exec rm -f {} +

    # Check if the __pycache__ directory exists and delete it and all its contents
    if [ -d "$MIGRATIONS_DIR/__pycache__" ]; then
        rm -rf "$MIGRATIONS_DIR/__pycache__"
        echo "Deleted __pycache__ directory and all its contents in $MIGRATIONS_DIR."
    fi

    echo "All migration files in $MIGRATIONS_DIR have been deleted, except for __init__.py."
}

delete_migrations "webhooks/migrations"

python manage.py makemigrations
python manage.py migrate

generate_superuser() {
    # Define the file to store the superuser password
    local PASSWORD_FILE=".django_superuser_password"

    # Check if the password file exists
    if [ ! -f "$PASSWORD_FILE" ]; then
        # Generate a random password
        DJANGO_SUPERUSER_PASSWORD=$(openssl rand -base64 32)

        # Save the password to the file
        echo "$DJANGO_SUPERUSER_PASSWORD" > "$PASSWORD_FILE"

        echo "Generated new Django superuser password and saved to $PASSWORD_FILE."
    else
        # Read the password from the file
        DJANGO_SUPERUSER_PASSWORD=$(cat "$PASSWORD_FILE")

        echo "Using existing Django superuser password from $PASSWORD_FILE."
    fi

    # Export the password as an environment variable
    DJANGO_SUPERUSER_PASSWORD="$DJANGO_SUPERUSER_PASSWORD" python manage.py createsuperuser --username=dev --email=dev@dev.com --noinput
}

generate_superuser

python manage.py load_fixtures

python manage.py runserver
