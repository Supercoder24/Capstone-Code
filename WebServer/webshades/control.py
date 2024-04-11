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
        print()
        print()
        print(request.json)
        print()
        print()   
        errors = []
        try:
            main_var = request.json['main']
            overrides = request.json['variables']
        except:     # great
            print('Incorrect information')
            errors.append('Incorrect information')
            returned = {
                'errors': errors
            }
            return returned 

        print('Overrides: ' + str(overrides))
        print('Main var: ' + str(main_var))
        last = db.execute("SELECT last_schedule FROM rooms WHERE roomname = ?",(name)).fetchone()

        if not overrides:
            errors.append('Override is required.')
        if not main_var:
            errors.append('Main is required.')

        if len(errors) > 0:
            print(errors)
            returned = {
                'errors': errors
            }
            return returned
        else:
            print(name)
            print()
            if db.execute('SELECT override, roomname FROM access INNER JOIN rooms ON rooms.id=access.room_id WHERE override=0 AND roomname=?',(name,)).fetchone() is not None:  #MAKE SURE TO CHANGE OVERRIDE WHEN OVERRIDDEN
                new_variables = ",".join([main_var if not _.isnumeric() else "m"+_ for _ in overrides])
                for i in range(len(new_variables.split(","))):
                    _ = new_variables.split(",")[i] if new_variables.split(",")[i]!="s" else "a"+last[0].split(",")[i] # Might work, might explode 50/50     If it does explode, it has to do with the last[0] and may be fixed by replacing it with last
                    if len(_)>=2 or _ == "s":
                        if (_[:1] in ["a","m"] and (int(_[1:]) <= 100 and int(_[1:]) >= 0)) or (_[:1] == "m" and int(_[1:]) >= -2 and int(_[1:])<=100) or _ == "s":
                            req = db.execute(
                                'SELECT id, ip, windows FROM access '
                                'INNER JOIN rooms ON rooms.id=access.room_id '
                                'WHERE user_id=? AND roomname=?', (g.user['id'], name)
                                ).fetchone()
                            if req is not None:
                                if len(new_variables.split(',')) != int(req['windows']):    
                                    print('Wrong number of variables!')
                                    errors.append('Wrong number of variables!')
                                    returned = {
                                        'errors': errors
                                    }
                                    return returned    
                                else:
                                    db.execute(
                                        'UPDATE rooms '
                                        'SET variables=?, main=? '
                                        'WHERE id=?', (",".join(overrides),main_var,req['id'])
                                        )
                                    db.commit()
                                    with open(current_app.config['VARIABLES'] + req['ip'] + '.txt', 'w') as file:
                                        file.write(new_variables)
                            returned = {
                                'errors': errors,
                                'success': 'Successfully updated room ' + name
                            }
                            return returned
                        else:      
                            print('Wrong format')
                            errors.append('Wrong format')
                            returned = {
                                'errors': errors
                            }
                            return returned        
            else:
                flash("Sorry, room {} is currently overwritten by the admins. If you think this is incorrect, feel free to send them a message.".format(name))
                print('Overwritten!')
                errors.append('Overwritten!')
                returned = {
                    'errors': errors
                }
                return returned            

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
        _ = db.execute(
            "SELECT rooms.id, event_name, tod, vars, countdown, schedule.room_id, user_id, roomname FROM schedule INNER JOIN access ON schedule.room_id=access.room_id INNER JOIN rooms on schedule.room_id=rooms.id WHERE user_id=? AND roomname=? ORDER BY countdown",(g.user["id"],name)
        ).fetchall() # List of tuples
        schedule = {}
        schedule['name'] = _[0][0] if len(_) > 0 else 'None'
        schedule['variables'] = _[0][3] if len(_) > 0 else ''
        # schedule['now'] = exec_data(name)['now']
        schedule['events'] = [item['event_name'] for item in _]
        
        
   # schedule = {
   #     "name": "Ha", # Name of the current event - from Cole                     
   #     "variables": 'm100', # Variables for the current event - from Cole        X
   #     'now': 'Tuesday Feb 27, 2024', # Date formatting                          X
   #     'events': [
   #         '9:15 Social Engineering', # [id, stringOfName, stringOfTime, stringOfDaysofWeek] # binary for days of week (mon, tues, wed...)
   #         '10:20 Social Engineering'
   #     ]
   # }
        schedule = exec_data(name)
        print('Schedule: ' + str(schedule))
    return render_template('control/room.html', room=room, schedule=schedule)

@bp.route('/auth/override', methods=('GET','POST'))
@login_required
def override():         #Check override = True/False before updating room controls
    db = get_db()
    if request.method == 'POST':
        main_var = request.json['main']
        new_variables = request.json['variables']
        error = None

        if not new_variables:
           error = 'New variables are required.'

        if error is not None:
           flash(error)
        else:
            req = db.execute(
                'SELECT user_id, admin FROM users'
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
        main_var = request.json['main']
        new_variables = request.json['variables']
        error = None

        if not new_variables:
           error = 'New variables are required.'

        if error is not None:
           flash(error)
        else:
            req = db.execute(
                'SELECT user_id, admin FROM users'
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
    if request.method == 'POST':
        db = get_db()
        days = request.json['days']
        tod = request.json['tod'] #Time of day
        new_variables = request.json['variables']
        event_name = request.json['eventName']
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
                                    db.execute('INSERT INTO schedule(room_id,countdown,day_string,vars,tod,event_name) VALUES (?, ?, ?, ?, ?, ?)',(req['id'],start_countdown(days,tod,new_variables),days,new_variables,tod,event_name))
                                    db.commit()
    
        _ = db.execute(
            "SELECT rooms.id, event_name, tod, vars, countdown, schedule.room_id, user_id, roomname FROM schedule INNER JOIN access ON schedule.room_id=access.room_id INNER JOIN rooms on schedule.room_id=rooms.id WHERE user_id=? AND roomname=? ORDER BY countdown",(g.user["id"],name)
        ).fetchall() # List of tuples
        schedule = {}
        # schedule['name'] = _[0][0] if len(_) > 0 else 'None'
        # schedule['variables'] = _[0][3] if len(_) > 0 else ''
        # # schedule['now'] = exec_data(name)['now']
        # schedule['events'] = [item['event_name'] for item in _]
        # schedule = exec_data(name) # Eventually return the new schedule
        return schedule
    return redirect('/')

@bp.route("/room/<name>/<eventname>/editevent",methods = ('GET','POST'))
@login_required
def edit_event(name,event_name):
    if request.method == 'POST':
        db = get_db()
        req = db.execute('SELECT days,tod,new_variables FROM schedule INNER JOIN rooms ON rooms.id = schedule.room_id WHERE event_name=? AND roomname = ?',(event_name,name))
        days = request.json['days'] if request.json['days'] else req["days"]
        tod = request.json['tod'] if request.json['tod'] else req["tod"]#Time of day 
        new_variables = request.json['variables'] if request.json['variables'] else req["variables"]
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
                                    db.execute('UPDATE schedule SET room_id=?,countdown=?,day_string=?,vars=?,tod=?) VALUES ?',(req['id'],start_countdown(days,tod,new_variables),days,new_variables,tod))
                                    db.commit()
        
        _ = db.execute(
            "SELECT rooms.id, event_name, tod, vars, countdown, schedule.room_id, user_id, roomname FROM schedule INNER JOIN access ON schedule.room_id=access.room_id INNER JOIN rooms on schedule.room_id=rooms.id WHERE user_id=? AND roomname=? ORDER BY countdown",(g.user["id"],name)
        ).fetchall() # List of tuples
        schedule = {}
        schedule['name'] = _[0][0] if len(_) > 0 else 'None'
        schedule['variables'] = _[0][3] if len(_) > 0 else ''
        schedule['now'] = exec_data(name)['current_time']
        return schedule
    return redirect('/')

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
                'SELECT user_id, admin FROM users'
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
