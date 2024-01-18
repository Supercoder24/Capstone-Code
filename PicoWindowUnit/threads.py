import _thread
import utime

var = 3

def second_thread():
    global var
    i = 0
    while i < 30 and var:
        print("Run " + str(i) + ": " + str(var))
        i += 1
        utime.sleep(1)
    print('Done!')

_thread.start_new_thread(second_thread, ())