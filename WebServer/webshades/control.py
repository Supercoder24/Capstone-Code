from flask import (
    Blueprint, flash, current_app, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webshades.auth import login_required
from webshades.db import get_db

bp = Blueprint('control', __name__) # No URL prefix, so based on /

@bp.route('/')
@login_required
def index():
    db = get_db()
    print('Id: ' + str(g.user['id']))
    request = db.execute(
        'SELECT roomname FROM access JOIN rooms ON rooms.id=access.room_id'
        ' WHERE user_id=? ORDER BY last_accessed DESC', (g.user['id'],)
    ).fetchone()
    if request == None:
        return redirect(url_for('auth.new'))
    else:
        roomname = request['roomname']
    # posts = db.execute(
    #     'SELECT p.id, title, body, created, author_id, username'
    #     ' FROM post p JOIN user u ON p.author_id = u.id' # Join combines the post contents from post with the author details from user
    #     ' ORDER BY created DESC' # Shows must recent first
    # ).fetchall() # Gets all results as a list of rows
    # TODO: Error handler if roomname not found
        return redirect(url_for('control.room', name=roomname))

@bp.route('/room/<name>', methods=('GET','POST'))
@login_required
def room(name):
    db = get_db()
    if request.method == 'POST':
        new_variables = request.form['variables']
        error = None

        if not new_variables:
            error = 'New variables are required.'

        if error is not None:
            flash(error)
        else:
            for _ in new_variables.split(","):
        req = db.execute(
        'SELECT user_id, room_id, roomname FROM access '
        'INNER JOIN rooms ON access.room_id = rooms.id '
        'WHERE user_id = ? AND roomname=?', (g.user['id'],name)
    ).fetchone()
        if req is not None:
            if len(_)>=2:
                if (_[:1] in ["a","m"] and (int(_[1:]) <= 100 and int(_[1:]) >= -2)):
                    req = db.execute(
                        'SELECT id, ip, windows FROM access '
                        'INNER JOIN rooms ON rooms.id=access.room_id '
                        'WHERE user_id=? AND roomname=?', (g.user['id'], name)
                    ).fetchone()
                    if req is not None:
                        if len(new_variables.split(',')) != int(req['windows']):
                            flash('Not enough variables!')
                        else:
                            db.execute(
                                'UPDATE rooms '
                                'SET variables=? '
                                'WHERE id=?', (new_variables,req['id'])
                            )
                            db.commit()
                            with open(current_app.config['VARIABLES'] + req['ip'] + '.txt', 'w') as file:
                                file.write(new_variables)


    room = db.execute(
        'SELECT id, roomname, ip, picos, windows, variables FROM access '
        'INNER JOIN rooms ON rooms.id=access.room_id '
        'WHERE user_id=? AND roomname=?', (g.user['id'], name)
    ).fetchone()
    if room == None:
        # Throw error and redirect
        return redirect(url_for('auth.new'))
    else:
        db.execute(
            'UPDATE access '
            'SET last_accessed=current_timestamp '
            'WHERE user_id=? and room_id=?', (g.user['id'], room['id'])
        )
        db.commit()
    return render_template('control/room.html', room=room)


#@bp.route('/create', methods=('GET', 'POST')) # Works the same way as /register in auth.py
#@login_required # Decorator defined in auth.py will redirect to login if not logged in
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

# To be used in update and delete views
# Gets post data by id and also checks if author = logged in user
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.") # Abort returns the corresponding HTTP status code 404 = Not Found

    if check_author and post['author_id'] != g.user['id']:
        abort(403) # 403 = Forbidden

    return post

# To access this route elsewhere, must provide arguments: Ex: url_for('blog.update', id=post['id'])
#@bp.route('/<int:id>/update', methods=('GET', 'POST')) # Takes one argument, the integer id (string by default without int:)
#@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?' # UPDATE rather than INSERT
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

#@bp.route('/<int:id>/delete', methods=('POST',)) # Only handle post as no actual view. Redirects to index instead
#@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
