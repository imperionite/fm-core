# fm-core: CLI Commands


```sh
# Django/DRF
# initial automation DRF app
./build_dev.sh
## delete and re-create new virtual env if environment is not detected by VS Code
# reinstall the packages again
$ python -m venv .venv # create
$ source .venv/bin/activate # activate
$ deactivate # deactivate

# install dependencies (backend)
pip install dependency_name

# creating backend project
django-admin startproject core .

# creating backend local apps
python manage.py startapp app_name

# create and apply migration
$ python manage.py makemigrations --dry-run --verbosity 3 # dry-run
$ python manage.py makemigrations
python manage.py migrate --fake-initial # mark initial migrations as applied without trying to recreate tables.
python manage.py migrate --no-input

# creating super user
python manage.py createsuperuser
# create superuser in command base
python manage.py create_superuser

# serve backend at localhost:8000
unset CI_TESTING # only if the pytest has run and initially in test mode
pip cache purge
python manage.py runserver

# generating requirements file
pip freeze > requirements.txt

# create secret keys
$ python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# running fixture, for initial run only, when flush DB or on intial deployment setup, 
# just delete first the initial_data.json in fixtures directory to generate new one
python manage.py generate_fixture_data 
# python connectly-api/manage.py loaddata connectly-api/posts/fixtures/initial_data.json

# assign roles to seeded user data
python manage.py assign_roles

# remove all records from the entire database (including resetting auto-incrementing primary keys)
python manage.py flush

# Render start command
gunicorn --workers 3 --bind 0.0.0.0:$PORT core.wsgi:application # the core folder is in the root repo

# Render build command
./build.sh

# ensure excution permission on all .sh files
chmod +x build_dev.sh # for DRF debug
chmod +x build.sh # for render.com
chmod +x K6/run_k6_tests.sh # for K6 load testing

# Site settings (Debug)
site.domain = 'localhost:8000'
site.name = 'Local Dev'

# Site settings (Prod)
site.domain = 'yourapp.onrender.com' # (No http/https, no trailing slashes)
site.name = 'App Name'

# K6
./build.sh # run the script on render
./build_dev.sh # run to build DRF on debug mode
./K6/run_k6_tests.sh # run to automate the K6 load testing


# https://marmite.onrender.com


# Checking Inside a Running PostgreSQL Docker Container
docker ps
docker exec -it [postgres_container_id] bash
psql -U myuser mydatabase
\! clear # clear screen
\dt # list tables
\dt public.* # list all tables in public schema
\dt * # list tables from all schema
\dt posts_user # specific table
SELECT * FROM posts_user;
SELECT id, username, email, password, created_at, date_joined, is_staff FROM posts_user;
\q # quit psql

# redis inside docker container
docker ps
docker exec -it <redis_container_name> redis-cli
AUTH mypassword
ping
# will return PONG

# Celery
# run celery from Django root directory
celery -A core worker --loglevel=info

# Pytest
export CI_TESTING="True" # export only on initial run
pip cache purge && pytest --cov --tb=short
pytest --cov --tb=short --cov-report=term-missing > test_log.txt 2>&1 # print to test_log.txt
```