from flask import (
    Blueprint, flash, current_app, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webshades.schedule_countdown import start_countdown, exec_data
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
        main_var = request.form['main']
        new_variables = request.form['variables']
        error = None

        if not new_variables:
            error = 'New variables are required.'

        if error is not None:
            flash(error)
        else:
            if db.execute('SELECT override INNER JOIN rooms ON rooms.id=access.room_id WHERE override = True AND roomname=?',(name)) is not None:  #MAKE SURE TO CHANGE OVERRIDE WHEN OVERRIDDEN
                new_variables = ",".join([main_var if not _.isnumeric() else "m"+_ for _ in new_variables])
                for _ in new_variables.split(","):
                    if len(_)>=2 or _ == "s":
                        if (_[:1] in ["a","m"] and (int(_[1:]) <= 100 and int(_[1:]) >= 0)) or (_[:1] == "m" and int(_[1:]) >= -2 and int(_[1:])<=100) or _ == "s":
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
                                        'SET variables=?, main=? '
                                        'WHERE id=?', (new_variables,main,req['id'])
                                        )
                                    db.commit()
                                    with open(current_app.config['VARIABLES'] + req['ip'] + '.txt', 'w') as file:
                                        file.write(new_variables)
                        else: flash("Input not in the correct format.")                
            else:
                flash("Sorry, room {} is currently overwritten by the admins. If you think this is incorrect, feel free to send them a message.".format(name))
                

    room = db.execute(
        'SELECT id, roomname, main, windows, variables FROM access '
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
        main_var = request.form['main']
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
                new_variables = ",".join([main_var if not _.isnumeric() else "m"+_ for _ in new_variables])
                for _ in new_variables.split(","):
                    if len(_)>=2:
                        if (_[:1] in ["a","m"] and (int(_[1:]) <= 100 and int(_[1:]) >= 0)) or (_[:1] == "m" and int(_[1:]) >= -2 and int(_[1:])<=100) or _ == "s":
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
            'SELECT id, roomname, main, windows, variables FROM access '
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
        main_var = request.form['main']
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
                new_variables = ",".join([main_var if not _.isnumeric() else "m"+_ for _ in new_variables])
                for _ in new_variables.split(","):
                    if len(_)>=2:
                        req = db.execute(
                                'SELECT id, ip, windows FROM access '
                                'INNER JOIN rooms ON rooms.id=access.room_id '
                                'WHERE user_id=? AND roomname=?', (g.user['id'], name)
                                ).fetchone()
                        if req is not None:
                            if (_[:1] in ["a","m"] and (int(_[1:]) <= 100 and int(_[1:]) >= 0)) or (_[:1] == "m" and int(_[1:]) >= -2 and int(_[1:])<=100) or _=="s":
                                if len(new_variables.split(',')) != int(req['windows']):
                                    flash('Not enough variables!')
                                else:
                                    with open(current_app.config['VARIABLES'] + req['ip']+'.txt','w') as file:
                                        file.write(new_variables)
                            else: flash("Input not in the correct format.")
                    else: flash("Input not in the correct format.")
            else: flash("User {} does not have permissions to perform this action.".format(db.execute('SELECT username FROM users WHERE id=?',(g.user['id']))))
    room = db.execute(
            'SELECT id, roomname, main, windows, variables FROM access '
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

@bp.route('/room/<name>/newschedule', methods = ('GET','POST'))
@login_required
def new_schedule(name):
    db = get_db()
    if request.method == 'POST':
        days = request.form['days']
        tod = request.form['tod'] #Time of day
        new_variables = request.form['variables']
        error = None

        if not new_variables:
           error = 'New variables are required.'

        if error is not None:
           flash(error)
        else:
            for _ in new_variables.split(","):
                if len(_)>=2:
                    req = db.execute(
                                'SELECT id, ip, windows FROM access '
                                'INNER JOIN rooms ON rooms.id=access.room_id '
                                'WHERE user_id=? AND roomname=?', (g.user['id'], name)
                                ).fetchone()
                    if req is not None:
                                if len(new_variables.split(',')) != int(req['windows']):
                                    flash('Not enough variables!')
                                else:
                                    db.execute('INSERT INTO schedule(room_id,countdown,days,vars,tod) VALUES ?',(req['id'],start_countdown(days,tod,new_variables),days,new_variables,tod))
                                    db.commit()

@bp.route("/room/<name>/<eventname>/editevent",methods = ('GET','POST'))
@login_required
def edit_event(name,event_name):
    db = get_db()
    if request.method == 'POST':
        req = db.execute('SELECT days,tod,new_variables FROM schedule INNER JOIN rooms ON rooms.id = schedule.room_id WHERE event_name=? AND roomname = ?',(event_name,name))
        days = request.form['days'] if request.form['days'] else req["days"]
        tod = request.form['tod'] if request.form['tod'] else req["tod"]#Time of day 
        new_variables = request.form['variables'] if request.form['variables'] else req["variables"]
        error = None

        if not new_variables:
           error = 'New variables are required.'

        if error is not None:
           flash(error)
        else:
            for _ in new_variables.split(","):
                if len(_)>=2:
                    req = db.execute(
                                'SELECT id, ip, windows FROM access '
                                'INNER JOIN rooms ON rooms.id=access.room_id '
                                'WHERE user_id=? AND roomname=?', (g.user['id'], name)
                                ).fetchone()
                    if req is not None:
                                if len(new_variables.split(',')) != int(req['windows']):
                                    flash('Not enough variables!')
                                else:
                                    db.execute('UPDATE schedule SET room_id=?,countdown=?,days=?,vars=?,tod=?) VALUES ?',(req['id'],start_countdown(days,tod,new_variables),days,new_variables,tod))
                                    db.commit()

@bp.route("/room/<name>/<eventname>/deleteevent",methods = ('GET','POST'))
@login_required
def delete_event(name,event_name):
    if request.method == 'POST':
        error = None

        if error is not None:
           flash(error)
        else:
            req = db.execute('SELECT id, event_name FROM schedule INNER JOIN rooms ON rooms.id=schedule.room_id WHERE roomname = ? AND event_name = ?',(name,event_name))
            db.execute('DELETE FROM schedule WHERE event_name = ? AND id = ?',(event_name,req['id']))
            db.commit()

@bp.route("/room/<name>/getschedule", methods = ('GET','POST'))
@login_required
def get_events(name):
    if request.method == 'POST':
        error = None

        if error is not None:
           flash(error)
        else:
            sched_dict = exec_data(name)
            # Do stuff with it mebbe
    return render_template('control/room.html', schedule=sched_dict)
@bp.route('/auth/create', methods=('GET','POST'))
@login_required
def new_room():
    db = get_db()
    if request.method == 'POST':
        specs = [request.form['roomname'],request.form['ip'],request.form['windows']]
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
                    specs.append(",".join(["m-1" for _ in range(specs[2])]))
                    db.execute('INSERT INTO rooms(roomname,ip,windows) VALUES ?',(specs)) # I may not work when you run me
                    db.commit()
                else:
                    flash("A room already exists with that name.")
            else: flash("User {} does not have permissions to perform this action.".format(db.execute('SELECT username FROM users WHERE id=?',(g.user['id']))))
    return render_template('auth/new.html')

