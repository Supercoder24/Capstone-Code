from machine import Pin
import utime
import ThreadStep as ThreadStep

id = 0 # Change to 1 for second unit

def typ():
    return 'wu' + str(0) # Window Unit

steps = {
    'm0': int(3 * 0.8 * 1024), # 4096 half steps per rev / 4 = 90 deg of steps
    'm1': int(3 * 0.8 * 1024) # 4096 half steps per rev / 4 = 90 deg of steps
}
dirs = {
    'm0': 1, # TODO: 1 = CW or CCW ?
    'm1': 1 # TODO: 1 = CW or CCW ?
}
MOTOR0 = ThreadStep.MOTOR0
MOTOR1 = ThreadStep.MOTOR1

m0pins = (Pin(2,Pin.OUT),
    Pin(3,Pin.OUT),
    Pin(4,Pin.OUT),
    Pin(5,Pin.OUT))

m1pins = (Pin(6,Pin.OUT),
    Pin(7,Pin.OUT),
    Pin(8,Pin.OUT),
    Pin(9,Pin.OUT))

ThreadStep.configure(m0pins, m1pins, steps, dirs)

def cfg_steps(mot, val):
    global steps
    steps[mot] = val
    ThreadStep.configure(m0pins, m1pins, steps, dirs)

def cfg_dir(mot, dir):
    global dirs
    dirs[mot] = dir
    ThreadStep.configure(m0pins, m1pins, steps, dirs)

def stat(val):
    if val == 'm0o':
        return ThreadStep.status['m0']['operation']
    if val == 'm1o':
        return ThreadStep.status['m1']['operation']
    if val == 'm0r':
        return ThreadStep.status['m0']['running']
    if val == 'm1r':
        return ThreadStep.status['m1']['running']
    if val == 'm0p':
        position = ThreadStep.status['m0']['position']
        if position <= 0:
            return position
        else:
            return position/steps['m0'] * 100
    if val == 'm1p':
        position = ThreadStep.status['m1']['position']
        if position <= 0:
            return position
        else:
            return position/steps['m1'] * 100
    return 'unknown'
    
def pos(motor, position):
    if position == -1:
        ThreadStep.stop(motor)
        return 'stopped'
    elif position >= 0 and position <= 100:
        ThreadStep.tilt(motor, int((position/100.0 * steps[motor]) / 8) * 8)
        return 'tilting' + str(int((position/100.0 * steps[motor]) / 8) * 8)
    else:
        return 'INVALID'
    
def cal(motor, dir, steps=100):
    ThreadStep.cal(motor, int((dir * steps)))