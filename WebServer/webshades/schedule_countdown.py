import time
from datetime import datetime, timedelta
#Every wednesday at 17:00
target_day = "Wednesday"
time_of_execution = "5:00"
time_of_execution = time_of_execution.split(":")
am_or_pm = "PM"
time_of_execution[0] = str(int(time_of_execution[0]) + (12 if am_or_pm.lower() == "pm" else 0))
dt = datetime.now()-timedelta(hours=6) #Date & time CST (default: GMT)
today = dt.weekday()
dt = str(dt)
time_list = dt[0:10].split("-")+dt[11:19].split(":")
week_list = ["monday", "tuesday", "wednesday", "thursday", "friday","saturday", "sunday"]
day = week_list.index(target_day.lower())
delta = timedelta(days=(day-today)%7,hours=int(time_of_execution[0])-int(time_list[3]),minutes=int(time_of_execution[1])-int(time_list[4]),seconds=0-int(time_list[5]))
print(datetime.now()-timedelta(hours=6)+delta)
seconds_until = delta - timedelta(hours=6)
print(seconds_until.total_seconds())
