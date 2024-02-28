import functools

from flask import (
    Blueprint, flash, current_app, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from webshades.db import get_db

# Creates a Blueprint called auth (way to organize related views and code)
bp = Blueprint('auth', __name__, url_prefix='/auth') # url_prefix is prepended to all views in this blueprint

@bp.route('/register', methods=('GET', 'POST')) # associated with /register of auth blueprint, so /auth/register
def register():
    if request.method == 'POST': # Submitted form data
        username = request.form['username'] # request.form is a dict mapping of keys and values
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (username, password, admin) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), False), # generate_password_hash is important
                ) # db library automatically prevents injection attacks
                db.commit() # MUST COMMIT CHANGES after executing a modification to the database
                user = db.execute(
                    'SELECT * FROM users WHERE username = ?', (username,)
                ).fetchone()
                if user is not None:
                    user_id = user['id']
            except db.IntegrityError: # Occurs if username already exists
                error = f"User {username} is already registered."
            else:
                # Redirect to login page if everything is successful
                return redirect(url_for("auth.login")) # url_for returns auth.login's url, in case it is ever changed

        flash(error) # Stores messages for the template to use during rendering

    # Shows register page if first time or again if there is an error
    return render_template('auth/register.html') # Renders data into the provided HTML template

@bp.route('/login', methods=('GET', 'POST')) # /auth/login
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone() # Returns a singular returned row from the query (or None if no results)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password): # same hashing as during registration
            error = 'Incorrect password.'

        if error is None:
            session.clear() # Session is a dict that stores data across requests
            session['user_id'] = user['id'] # Session data is stored in a cookie and signed to prevent tampering
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request # Registers a function to run before the view function, for any URL
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone() # Makes user data from database accessible to all other functions during the request duration
        req = db.execute(
            'SELECT roomname FROM access '
            'INNER JOIN rooms ON rooms.id=access.room_id '
            'WHERE user_id=? ORDER BY roomname ASC', (user_id,)
        ).fetchall()
        if req is not None:
            print('Found rooms')
            print(req)
            g.rooms = [row['roomname'] for row in req]
            print(g.rooms)
        else:
            g.rooms = []

@bp.route('/logout')
def logout():
    session.clear() # Removes the user data from the session cookie, so can no longer use or validate with user data
    return redirect(url_for('index'))

# Decorator that can be used to wrap other views
def login_required(view):
    @functools.wraps(view)
    # Redirects to login page if not logged in
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/new', methods=('GET', 'POST'))
@login_required
def new():
    if request.method == 'POST': # Submitted form data
        roomname = request.form['roomname']
        ip = request.form['ip']
        windows = request.form['windows']
        db = get_db()
        error = None

        if error is None:
            user_id = g.user['id']
            room_id = None
            try:
                variables = ','.join(['' for i in range(int(windows))])
                main = 'm-1'
                print('Vars: ' + variables)
                db.execute(
                    "INSERT INTO rooms (roomname, ip, windows, override, main, variables) VALUES (?, ?, ?, ?, ?, ?)",
                    (roomname, ip, int(windows), False, main, variables)
                )
                db.commit()
                new_variables = ",".join([main if not _.isnumeric() else "m"+_ for _ in variables])
                with open(current_app.config['VARIABLES'] + ip + '.txt', 'w') as file:
                    file.write(new_variables)
                room = db.execute(
                    'SELECT * FROM rooms WHERE roomname = ?', (roomname,)
                ).fetchone()
                if room is not None:
                    room_id = room['id']
            except db.IntegrityError:
                error = f"Room {roomname} is already created."
            else:
                if user_id is not None and room_id is not None:
                    db.execute(
                        "INSERT INTO access (user_id, room_id) VALUES (?, ?)",
                        (user_id, room_id)
                    )
                    db.commit()
                    req = db.execute(
                        'SELECT ip FROM rooms'
                    ).fetchall()
                    if req is not None:
                        pi_ips = ','.join([room['ip'] for room in req])
                        with open(current_app.config['VARIABLES'] + 'pi_ips', 'w') as file:
                            file.write(pi_ips)
                    # Redirect to login page if everything is successful
                    return redirect(url_for("control.index")) # url_for returns auth.login's url, in case it is ever changed

        flash(error) # Stores messages for the template to use during rendering

    # Shows register page if first time or again if there is an error
    return render_template('auth/new.html') # Renders data into the provided HTML template
