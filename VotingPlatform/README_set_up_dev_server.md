# Set up an Deeva Voting Platform developper server

This sums up the steps to set up a development server for the *Deeva* voting platform. It is expected that **Python 3** and a **MySQL** server are already installed.


## Set up a virtual environment

It is strongly recommended to work in a virtual environment while developing for the platform. It ensures a fixed environment of available packages that everyone can rely on.

1. Install the virtual environment package if not done yet: `pip3 install virtualenv`
1. Create a new environment with `python3 -m venv deeva3`
1. Activate the environment with `source ./deeva3/bin/activate`
1. Sometimes Python Wheel is needed for the install of some packages. Install it with `pip install wheel`


## Install required packages

Install the packages required to run the voting platform by running:
```
pip install -r requirements.txt
```

Remember to crete a new package list when adding required packages by running:
```
pip freeze > requirements.txt` and pushing the file to the repository.
```

Currently running Ubuntu the `mysqlclient` package is not working correctly, you additionally need to install it via the systems package manager:
```
sudo apt-get install python3-dev libmysqlclient-dev
```

## Set up the database server

The website needs a database and database access in order to work correctly.
Currently it is setup to work with *MySQL*.
The connection data the system uses can be found in `deeva/deeva/setting.py` in the variable `DATABASES`.

In order to set up the database with the current code proceed as follows:

1. The MySQL deamon needs to be running (Ubuntu: `sudo service mysql start`)
1. Open the MySQL console and log in as privileged user: `mysql -u root -p`
1. Create the new database schema for developing : `CREATE SCHEMA deeva_dev;` (dont forget the semicolon...)
1. Switch to the newly created schema: `USE deeva_dev;`
1. Grant privileges for the django to access the database: `GRANT ALL PRIVILEGES ON deeva_dev.* to deeva@localhost identified by '123';`.
1. Exit the MySQL console.

## Create tables on the server

Django will alter table on the MySQL server by issuing the `migrate` and `makemigrations` command.
On the first run it will create them.
In the project folder `deeva`, where the `manage.py` file is located, run, in order:
  * `python manage.py makemigrations`
  * `python manage.py migrate`

Also, every time you alter the DJango tables, you must re-issue the `makemigrations`.
Finally, every time you pull from git and someone else altered the tables, you must re-issue `migrate`

## Create a django-root user

```
$ python manage.py createsuperuser
Username (leave blank to use 'fanu01'): admin
Email address:
Password:
Password (again):
```

## Run the development server

Finally to run the development server run:
```
python manage.py runserver
```
and it will create a locally accessible server on port 8000.
You can specify that it accessible from other computers or change the port like so:
```
pyhton manage.py runserver 0.0.0.0:8000
```



## Login as administrator

This is needed if you want to create new experiments.
With your browser, go to: `http://localhost:8000/admin`

# Development extras

## Generate UML graphs

How to create Entity-Relation Diagrams (ERD) from existing Django models.
Taken from: https://stackoverflow.com/questions/6776592/django-model-graphic-representation-erd

Install the django extensions:
```
pip install django-extensions
```

and graphviz:
```
pip install pygraphviz
```

Update the configuration `deeva/settings.py`:
```
INSTALLED_APPS = (
    ...
    'django_extensions',
)
```

Now run:
```
python manage.py graph_models experiments questions news | dot -Tpdf > ../Docs/VotingPlatform-ERD.pdf
```
