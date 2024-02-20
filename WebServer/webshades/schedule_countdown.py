import time
from datetime import datetime, timedelta
from webshades.db import get_db
def exec_data(name):
  dictionary = {}
  db = get_db()
  req = db.execute('SELECT event_name, tod, days FROM schedule INNER JOIN rooms. id=schedule.room_id WHERE roomname = ?',(name))
  dt = datetime.now()-timedelta(hours=6) #Date & time CST (default: GMT)
  dictionary["current_time"] = str((datetime.now()-timedelta(hours=6)).weekday()) + " " + str(datetime.now()-timedelta(hours=6))[0:10]
  for _ in req:
    dictionary[req[event_name]] = (str(req[tod]%12)+"pm" if tod[:2].isnumeric() and int(tod[:2])>=12 else str(req[tod])+"am") + (["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][((datetime.now()-timedelta(hours=6)).weekday()+(([*(req["days"]+req["days"])[(datetime.now()-timedelta(hours=6)).weekday():]+(req["days"]+req["days"])[:(datetime.now()-timedelta(hours=6)).weekday()]]).index("1") if timedelta(days=(([*(req["days"]+req["days"])[(datetime.now()-timedelta(hours=6)).weekday():]+(req["days"]+req["days"])[:(datetime.now()-timedelta(hours=6)).weekday()]])).index("1"),hours=int(tod.split(":")[0])-int(dt[0:10].split("-")+dt[11:19].split(":")[3]),minutes=int(tod.split(":")[1])-int(dt[0:10].split("-")+dt[11:19].split(":")[4]),seconds=0-int(dt[0:10].split("-")+dt[11:19].split(":")[5])).total_seconds() else ([*(req["days"]+req["days"])[(datetime.now()-timedelta(hours=6)).weekday():]+(req["days"]+req["days"])[:(datetime.now()-timedelta(hours=6)).weekday()].replace("1","0", 1)].index("1"))))%7])
    
def start_countdown(input_list, time_of_execution, event_lapsed = False):
  t = time_of_execution
  i = input_list
  time_of_execution = time_of_execution.split(":")
  dt = datetime.now()-timedelta(hours=6) #Date & time CST (default: GMT)
  today = dt.weekday()
  input_list+=input_list
  changed_numbers = input_list[today:]+input_list[:today] if not event_lapsed else (input_list[today:]+input_list[:today]).replace("1","0", 1)
  target_day = [*changed_numbers].index("1")
  dt = str(dt)
  time_list = dt[0:10].split("-")+dt[11:19].split(":")
  delta = timedelta(days=target_day,hours=int(time_of_execution[0])-int(time_list[3]),minutes=int(time_of_execution[1])-int(time_list[4]),seconds=0-int(time_list[5]))
  print(datetime.now()-timedelta(hours=6)+delta)
  seconds_until = delta - timedelta(hours=6)
  if int(seconds_until.total_seconds())<0:
    start_countdown(input_list,t, True)
  else:
    next_occurrence = time.time()+int(seconds_until.total_seconds())
    return next_occurrence

while True:
  min = db.execute('SELECT MIN(countdown) FROM schedule INNER JOIN rooms ON rooms.id = schedule.room_id WHERE main = s')
  if min < time.time():
    req = db.execute('SELECT days, vars, tod, ip FROM schedule INNER JOIN rooms ON rooms.id=schedule.room_id WHERE countdown = ?',(min)).fetchone()
    db.execute('UPDATE schedule SET countdown =? WHERE countdown = ? and vars=?',(start_countdown(req[0],req[2],True),min,req[1])
    db.execute('UPDATE rooms SET variables = ? WHERE ip = ?',(req[1],req[3])
    db.commit()
    with open(current_app.config['VARIABLES'] + req['ip'] + '.txt', 'w') as file:
                                        file.write(new_variables)
    continue
  time.sleep(30)
    
    
