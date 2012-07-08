Running test instance
=====================

After cloning the repository, install all requirements:

    $ pip install -f requirements.txt

,create a database (sqlite3 by default):

    $ make db

, and run development server:

    $ make run


Admin panel
-----------

Django's admin panel is available under `/_admin/` path:

    http://localhost:8000/_admin/

Password and login for default admin account are:

    login:    admin
    password: a
