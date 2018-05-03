# Installation and usage

- Install Docker (required for the Redis backend)
- Install Python 3+
- `pip install -r requirements.txt`
- `python manage.py makemigrations tracker`
- `python manage.py migrate`

# Running the app

The WebSocket implementation requires a Redis instance, this is easiest to satisfy with the redis Docker image.

- `docker run -p 6379:6379 -d docker:latest`

The site can be launched with `python manage.py runserver`.
Alternatively, if you want to tinker with the models, you can use `python manage.py shell`.

# Resetting the database and migrations

- Delete the `tracker/migrations` folder and `db.sqlite3`
- Run migrations again (the two commands in the installation section)
