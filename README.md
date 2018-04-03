# Installation and usage

- Install Python 3+
- `pip install -r requirements.txt`
- `python manage.py makemigrations tracker`
- `python manage.py migrate`

Run the interactive shell with `python manage.py shell` or the server with `python manage.py runserver`.

# Resetting the database and migrations

- `python manage.py migrate tracker zero`
- Delete the `tracker/migrations` folder
- Run migrations again (the two commands in the installation section)
