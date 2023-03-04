import psycopg2
from psycopg2 import Error
from dotenv import dotenv_values
from flask import current_app, g

config = dotenv_values()

def get_connection():
    try:
        # Connect to an existing database
        connection = psycopg2.connect(user="postgres",
                                    password=config['POSTGRES_PASSWORD'],
                                    host=config['POSTGRES_HOST'],
                                    port="5432",
                                    database=config['POSTGRES_DATABASE'])

        # Create a cursor to perform database operations
        cursor = connection.cursor()
        # Print PostgreSQL details
        print("PostgreSQL server information")
        print(connection.get_dsn_parameters(), "\n")
        return connection

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)

def get_db():
    if 'db' not in g:
        g.db = get_connection()
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        print("PostgreSQL connection is closed")

def init_app(app):
    app.teardown_appcontext(close_db)