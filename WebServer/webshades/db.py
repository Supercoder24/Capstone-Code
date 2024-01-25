import sqlite3

import click
from flask import current_app, g # g is a unique pseudo-global variable for saving data during a request


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'], # Connects to the file specified in configuration earlier
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row # Database will return dict formatted rows

    return g.db

# Closes database connection if exists
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# Runs commands found in schema.sql
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f: # open_resource opens a file relative to webshades (doesn't matter where webshades is on host)
        db.executescript(f.read().decode('utf8'))

# Defines the command line command init-db
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    click.echo(str(current_app.config['DATABASE']))
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db) # Call function when cleaning up after returning a response to a request
    app.cli.add_command(init_db_command) # Add new command to the flask command