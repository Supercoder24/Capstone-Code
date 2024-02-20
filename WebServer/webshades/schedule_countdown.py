import time
from datetime import datetime, timedelta
from webshades.db import get_db
def start_countdown(input_list, time_of_execution, event_lapsed = False):
  t = time_of_execution
  i = input_list
  time_of_execution = time_of_execution.split(":")
  dt = datetime.now()-timedelta(hours=6) #Date & time CST (default: GMT)
  today = dt.weekday()
  today = 5
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
  min = db.execute('SELECT MIN(countdown) FROM schedule')
  if min < time.time():
    req = db.execute('SELECT days, vars, tod, ip FROM schedule INNER JOIN rooms ON rooms.id=shedule.room_id WHERE countdown = ?',(min)).fetchone()
    db.execute('UPDATE schedule SET countdown =? WHERE countdown = ? and vars=?',(start_countdown(req[0],req[2],True),min,req[1])
    db.execute('UPDATE rooms SET variables = ? WHERE ip = ?',(req[1],req[3])
    db.commit()
    with open(current_app.config['VARIABLES'] + req['ip'] + '.txt', 'w') as file:
                                        file.write(new_variables)
    continue
  time.sleep(30)
    
    
