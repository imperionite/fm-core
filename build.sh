#!/usr/bin/env bash
# Exit on error
set -o errexit

# IMPORTANT: Ensure CI_TESTING is NOT set.
# This forces Django to use the 'else' block in settings.py for production configurations.
unset CI_TESTING

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Collect static files (needed for Django Admin and any other static assets)
python manage.py collectstatic --noinput


# Run makemigrations dry-run to detect errors or issues
echo "Checking for migration issues (dry run)..."
if ! python manage.py makemigrations --dry-run --verbosity 3 --check; then
  echo "Migration check failed! Please fix the issues before proceeding."
  exit 1
fi

# Apply database migrations
python manage.py makemigrations
python manage.py migrate --no-input

# Run the custom command to create super user, staff & seed initial regular users
python manage.py seed_initial_users

