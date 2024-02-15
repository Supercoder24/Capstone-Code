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
            if db.execute('SELECT override INNER JOIN rooms ON rooms.id=access.room_id WHERE override = True AND roomname=?',(name)) is not None:  #MAKE SURE TO CHANGE OVERRIDE WHEN OVERRIDDEN
                for _ in new_variables.split(","):
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
                        else: flash("Input not in the correct format.")                
            else:
                flash("Sorry, room {} is currently overwritten by the admins. If you think this is incorrect, feel free to send them a message.".format(name))
                

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

@bp.route('/auth/override', methods=('GET','POST'))
@login_required
def override():         #Check override = True/False before updating room controls
    db = get_db()
    if request.method == 'POST':
        new_variables = request.form['variables']
        error = None

        if not new_variables:
           error = 'New variables are required.'

        if error is not None:
           flash(error)
        else:
            req = db.execute(
                'SELECT user_id, admin FROM access'
                'WHERE user_id=? AND admin = True', (g.user['id'])
            ).fetchone()
            if req is not None:
                for _ in new_variables.split(","):
                    if len(_)>=2:
                        if (_[:1] in ["a","m"] and (int(_[1:]) <= 100 and int(_[1:]) >= -2)):
                            if len(new_variables.split(',')) != int(db.execute('SELECT MAX(windows) FROM rooms')):
                                flash('Not enough variables!')
                            else:
                                db.execute(
                                    'UPDATE rooms'
                                    'SET variables=?'
                                    'WHERE roomname=override', (new_variables)
                                )
                                db.commit()
                                with open(current_app.config['VARIABLES']+"pi_ips","r") as file:
                                    for host in file.read().split(","):
                                        req = db.execute(
                                            'SELECT windows FROM rooms WHERE ip=?', (host)
                                        )
                                        with open (current_app.config['VARIABLES'] + host + '.txt', 'w') as room_file:
                                            file.write(",".join(new_variables.split(",")[:req]))
                        else: flash("Input not in the correct format.")
                    else: flash("Input not in the correct format.")
        room = db.execute(
            'SELECT id, roomname, ip, picos, windows, variables FROM access '
            'INNER JOIN rooms ON rooms.id=access.room_id '
            'WHERE user_id=? AND roomname=override', (g.user['id'])
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
        
@bp.route('/room/<name>/override', methods=('GET','POST'))
@login_required
def override_individual(name):
    db = get_db()
    if request.method == 'POST':
        new_variables = request.form['variables']
        error = None

        if not new_variables:
           error = 'New variables are required.'

        if error is not None:
           flash(error)
        else:
            req = db.execute(
                'SELECT user_id, admin FROM access'
                'WHERE user_id=? AND admin = True', (g.user['id'])
            ).fetchone()
            if req is not None:
                for _ in new_variables.split(","):
                    if len(_)>=2:
                        req = db.execute(
                                'SELECT id, ip, windows FROM access '
                                'INNER JOIN rooms ON rooms.id=access.room_id '
                                'WHERE user_id=? AND roomname=?', (g.user['id'], name)
                                ).fetchone()
                        if req is not None:
                            if (_[:1] in ["a","m"] and (int(_[1:]) <= 100 and int(_[1:]) >= -2)):
                                if len(new_variables.split(',')) != int(req['windows']):
                                    flash('Not enough variables!')
                                else:
                                    with open(current_app.config['VARIABLES'] + req['ip']+'.txt','w') as fileL
                                        file.write(new_variables)
                            else: flash("Input not in the correct format.")
                    else: flash("Input not in the correct format.")
            else: flash("User {} does not have permissions to perform this action.".format(g.user['id']))
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

@bp.route('/auth/create', methods=('GET','POST'))
@login_required
def new_room():
    db = get_db()
    if request.method == 'POST':
        specs = [request.form['roomname'],request.form['ip'],request.form['picos'],request.form['windows']]
        error = None
        if not specs:
           error = 'New input are required.'

        if error is not None:
           flash(error)
        else:
            req = db.execute(
                'SELECT user_id, admin FROM access'
                'WHERE user_id=? AND admin = True', (g.user['id'])
            ).fetchone()
            if req is not None:
                if db.execute('SELECT id WHERE rooms.id=?',(specs[0])) is None:
                    specs.append(",".join(["m-1" for _ in range(specs[3])]))
                    db.execute('INSERT INTO rooms(roomname,ip,picos,windows) VALUES ?',(specs)) # I may not work when you run me
                    db.commit()
                else:
                    flash("A room already exists with that name.")
            else: flash("User {} does not have permissions to perform this action.".format(g.user['id']))
    return render_template('auth/new.html')

