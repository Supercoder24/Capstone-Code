from machine import Pin
import utime
import ThreadStep as ThreadStep

TILT_STEPS = 1024 # 4096 half steps per rev / 4 = 90 deg of steps
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

limitpins = (Pin(10,Pin.IN,Pin.PULL_UP), # upper limit switch
    Pin(11,Pin.IN,Pin.PULL_UP), # lower limit switch
    Pin(12,Pin.IN,Pin.PULL_UP),
    Pin(13,Pin.IN,Pin.PULL_UP),
)

ThreadStep.configure(m0pins, m1pins, limitpins, TILT_STEPS)

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
            return position/TILT_STEPS * 100
    if val == 'm1p':
        position = ThreadStep.status['m1']['position']
        if position <= 0:
            return position
        else:
            return position/TILT_STEPS * 100
    if val == 'm0l':
        return ThreadStep.limits['m0'][0].value() + ThreadStep.limits['m0'][1].value()
    if val == 'm1l':
        return ThreadStep.limits['m1'][0].value() + ThreadStep.limits['m1'][1].value()
    
def pos(motor, position):
    if position == -2:
        ThreadStep.retract(motor)
        return 'retracting'
    elif position < 100:
        if ThreadStep.status[motor]['position'] > -1:
            ThreadStep.tilt(motor, int((position/100.0 * TILT_STEPS) / 8) * 8)
            return 'tilting' + str(int((position/100.0 * TILT_STEPS) / 8) * 8)
        else:
            ThreadStep.extend(motor)
            return 'extending'
    elif position == 100:
        ThreadStep.extend(motor)
        return 'extending'