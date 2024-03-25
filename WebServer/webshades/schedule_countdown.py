import time
from datetime import datetime, timedelta
from webshades.db import get_db
import sqlite3
from flask import current_app
def exec_data(name):
  dictionary = {'events': []}
  db = get_db()
  req = db.execute('SELECT event_name, tod, roomname, day_string FROM schedule INNER JOIN rooms ON rooms.id=schedule.room_id WHERE roomname=?',(name,)).fetchall()
  dt = datetime.now()-timedelta(hours=6) #Date & time CST (default: GMT)
  dictionary["now"] = "{} {} {}, {}".format(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][dt.weekday()],["January","February","March","April","May","June","July","August","September","October","November","December"][dt.month-1],dt.day,dt.year) #+ " " + str(datetime.now()-timedelta(hours=6))[0:10]
  dictionary['name'] = 'No event selected'
  dictionary['variables'] = 'm50'
  # print(dt)
  for _ in req:
    dictionary['events'].append(_['tod'] + ' ' + _['event_name'])
    # dictionary['events'].append((
    #   str(_['tod']%12)+"pm" if _['tod'][:2].isnumeric() and int(_['tod'][:2])>=12 else str(_['tod'])+"am"
    # ) + (
    #   ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][(datetime.now()-timedelta(hours=6)).weekday()])) # Added (datetime.now()-timedelta(hours=6)).weekday()])
        # (
        #   (datetime.now()-timedelta(hours=6)).weekday() + 
        #   (([*(_["day_string"]+_["day_string"])[(datetime.now()-timedelta(hours=6)).weekday():]+
        #       (_["day_string"]+_["day_string"])[:(datetime.now()-timedelta(hours=6)).weekday()]]).index("1") if timedelta(
        #         days=(([*(_["day_string"]+_["day_string"])[(datetime.now()-timedelta(hours=6)).weekday():]+
        #           (_["day_string"]+_["day_string"])[:(datetime.now()-timedelta(hours=6)).weekday()]])).index("1"),
        #         hours=int(_['tod'].split(":")[0])-int(str(dt)[0:10].split("-")[2]+str(dt)[11:19].split(":")[0]),
        #         minutes=int(_['tod'].split(":")[1])-int(str(dt)[0:10].split("-")[2]+str(dt)[11:19].split(":")[1]),
        #         seconds=0-int(str(dt)[0:10].split("-")[2]+str(dt)[11:19].split(":")[2])
        #       ).total_seconds() else (
        #           [*(_["day_string"]+_["day_string"])[(datetime.now()-timedelta(hours=6)).weekday():]+
        #           (_["day_string"]+_["day_string"])[:(datetime.now()-timedelta(hours=6)).weekday()].replace("1","0", 1)].index("1"))))%7])
  return dictionary    
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

def count():
  db = sqlite3.connect(
              'var/webshades-instance/webshades.sqlite', # Connects to the file specified in configuration earlier
              detect_types=sqlite3.PARSE_DECLTYPES
          )
  db.row_factory = sqlite3.Row
  while True:
    min = db.execute('SELECT MIN(countdown) FROM schedule INNER JOIN rooms ON rooms.id = schedule.room_id WHERE main = s')
    if min < time.time():
      req = db.execute('SELECT day_string, vars, tod, ip FROM schedule INNER JOIN rooms ON rooms.id=schedule.room_id WHERE countdown = ?',(min)).fetchone()
      db.execute('UPDATE schedule SET countdown =? WHERE countdown = ? and vars=?',(start_countdown(req[0],req[2],True),min,req[1]))
      db.execute('UPDATE rooms SET variables = ? WHERE ip = ?',(req[1],req[3]))
      db.commit()
      with open('variables/' + req['ip'] + '.txt', 'w') as file:
                                          file.write(new_variables)
      continue
    time.sleep(30)

if __name__ == "__main__":
  count()
    
    
