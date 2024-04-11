"""
Library for running two stepper motor simultaneously on Core 1 of a Raspberry Pi Pico
Designed and implemented by Felix Airhart in 2024

Configuration:
* configure(m0pins, m1pins, ?tilt_hs_dur, ?fast_hs_dur)

Functions:
* tilt(motor, steps, ?hs_dur) (+ steps = closed)
* stop(motor)

Status:
* status
  * threaded (bool) is thread running
  * [motor]
    * job_id (int) which job is running
    * running (bool) is motor moving
    * operation (str) see operation reference
    * position (int) see position reference

All steps and hs variables in terms of half steps
"""

from machine import Pin
import _thread
import utime

TILT_HS_DUR = 0.005 # seconds per half step
FAST_HS_DUR = 0.001 # seconds per half step
steps = {
    'm0': 1024, # 4096 half steps per rev / 4 = 90 deg of steps
    'm1': 1024 # 4096 half steps per rev / 4 = 90 deg of steps
}
dirs = {
    'm0': 1, # TODO: 1 = CW or CCW ?
    'm1': 1 # TODO: 1 = CW or CCW ?
}

MOTOR0 = 'm0' # Counterclockwise = lower and tilt closed
MOTOR1 = 'm1' # Clockwise = lower and tilt closed

m0pins = (Pin(2,Pin.OUT),
    Pin(3,Pin.OUT),
    Pin(4,Pin.OUT),
    Pin(5,Pin.OUT))

m1pins = (Pin(6,Pin.OUT),
    Pin(7,Pin.OUT),
    Pin(8,Pin.OUT),
    Pin(9,Pin.OUT))

def configure(new_m0pins, new_m1pins, new_steps, new_dirs):
    global m0pins
    global m1pins
    global steps
    global dirs
    m0pins = new_m0pins
    m1pins = new_m1pins
    steps = new_steps
    dirs = new_dirs

# Position:
# * -1 in between, no idea where
# * 0 completely open
# * y where 0 < y < steps[motor] all the way down, tilted between open and closed
# * steps[motor] completely closed

# ONLY THREAD CAN WRITE
status = {
    'threaded': False,
    'm0': {
        'job_id': 0,
        'running': False,
        'operation': 'standby',
        'position': -1 # No idea where it is
    },
    'm1': {
        'job_id': 0,
        'running': False,
        'operation': 'standby',
        'position': -1 # No idea where it is
    }
}

def stat():
    print('Thread running: ' + str(status['threaded']))
    print('Motor0 running:\t' + str(status[MOTOR0]['running']) + '\tJob: ' + str(status[MOTOR0]['job_id']) + '\t' + str(status[MOTOR0]['operation']) + '\tPosition: ' + str(status[MOTOR0]['position']))
    print('Motor1 running:\t' + str(status[MOTOR1]['running']) + '\tJob: ' + str(status[MOTOR1]['job_id']) + '\t' + str(status[MOTOR1]['operation']) + '\tPosition: ' + str(status[MOTOR1]['position']))

def stat_feed():
    while True:
        stat()
        utime.sleep(1)

# Operations: 
# * standby (doing nothing)
# * opening (tilting towards horizontal)
# * closing (tilting towards vertical)

# THREAD CAN ONLY READ
jobs = {
    'quit': False, # set True to stop other thread
    'm0': {
        'id': 0, # Increments automatically. Resets every 1024
        'run': False, # set True to execute operation
        'operation': 'standby',
        'target': 0, # Tilting
        'tilt_hs_dur': TILT_HS_DUR,
        'fast_hs_dur': FAST_HS_DUR,
    },
    'm1': {
        'id': 0, # Increments automatically. Resets every 1024
        'run': False, # set True to execute operation
        'operation': 'standby',
        'target': 0, # Tilting
        'tilt_hs_dur': TILT_HS_DUR,
        'fast_hs_dur': FAST_HS_DUR,
    }
}

def run_cw(pins):
    pins[3].value(False)
    pins[1].value(True)
    utime.sleep(0.002)
    pins[0].value(False)
    pins[2].value(True)
    utime.sleep(0.002)
    pins[1].value(False)
    pins[3].value(True)
    utime.sleep(0.002)
    pins[2].value(False)
    pins[0].value(True)
    utime.sleep(0.002)

def run_ccw(pins):
    pins[0].value(False)
    pins[2].value(True)
    utime.sleep(0.002)
    pins[3].value(False)
    pins[1].value(True)
    utime.sleep(0.002)
    pins[2].value(False)
    pins[0].value(True)
    utime.sleep(0.002)
    pins[1].value(False)
    pins[3].value(True)
    utime.sleep(0.002)

def run_both_opp(pins_ccw, pins_cw):
    pins_cw[3].value(False)
    pins_ccw[0].value(False)
    pins_cw[1].value(True)
    pins_ccw[2].value(True)
    utime.sleep(0.002)
    pins_cw[0].value(False)
    pins_ccw[3].value(False)
    pins_cw[2].value(True)
    pins_ccw[1].value(True)
    utime.sleep(0.002)
    pins_cw[1].value(False)
    pins_ccw[2].value(False)
    pins_cw[3].value(True)
    pins_ccw[0].value(True)
    utime.sleep(0.002)
    pins_cw[2].value(False)
    pins_ccw[1].value(False)
    pins_cw[0].value(True)
    pins_ccw[3].value(True)
    utime.sleep(0.002)

def run_both_cw(pins0, pins1):
    pins0[3].value(False)
    pins1[3].value(False)
    pins0[1].value(True)
    pins1[1].value(True)
    utime.sleep(0.002)
    pins0[0].value(False)
    pins1[0].value(False)
    pins0[2].value(True)
    pins1[2].value(True)
    utime.sleep(0.002)
    pins0[1].value(False)
    pins1[1].value(False)
    pins0[3].value(True)
    pins1[3].value(True)
    utime.sleep(0.002)
    pins0[2].value(False)
    pins1[2].value(False)
    pins0[0].value(True)
    pins1[0].value(True)
    utime.sleep(0.002)

def run_both_ccw(pins0, pins1):
    pins0[0].value(False)
    pins1[0].value(False)
    pins0[2].value(True)
    pins1[2].value(True)
    utime.sleep(0.002)
    pins0[3].value(False)
    pins1[3].value(False)
    pins0[1].value(True)
    pins1[1].value(True)
    utime.sleep(0.002)
    pins0[2].value(False)
    pins1[2].value(False)
    pins0[0].value(True)
    pins1[0].value(True)
    utime.sleep(0.002)
    pins0[1].value(False)
    pins1[1].value(False)
    pins0[3].value(True)
    pins1[3].value(True)
    utime.sleep(0.002)

def off(pins):
    pins[0].value(False)
    pins[1].value(False)
    pins[2].value(False)
    pins[3].value(False)

# TODO: Choice: variable speeds for tilt and raise -or- consolidate speeds into 1 constant
def _stepperThread():
    global status
    global jobs
    doing = {
        'm0': {
            'id': 0, # Increments automatically. Resets every 1024
            'operation': 'standby',
            'target': 0, # Tilting
            'tilt_hs_dur': 0.001,
            'fast_hs_dur': 0.001,
            'runs': 0,
        },
        'm1': {
            'id': 0, # Increments automatically. Resets every 1024
            'operation': 'standby',
            'target': 0, # Tilting
            'tilt_hs_dur': 0.001,
            'fast_hs_dur': 0.001,
            'runs': 0,
        }
    }

    status['threaded'] = True
    # print('Stepper thread started')
    while not jobs['quit']:
        run = {
            'm0': 0,
            'm1': 0
        }
        for motor in (MOTOR0, MOTOR1):
            if jobs[motor]['id'] != doing[motor]['id']:
                doing[motor]['target'] = jobs[motor]['target']
                if jobs[motor]['operation'] == 'tilt':
                    if jobs[motor]['target'] > status[motor]['position']:
                        doing[motor]['operation'] = 'closing'
                        status[motor]['operation'] = 'closing'
                    elif jobs[motor]['target'] < status[motor]['position']:
                        doing[motor]['operation'] = 'opening'
                        status[motor]['operation'] = 'opening'
                    else:
                        doing[motor]['operation'] = 'standby'
                        status[motor]['operation'] = 'standby'
                else:
                    status[motor]['operation'] = jobs[motor]['operation']
                    doing[motor]['operation'] = jobs[motor]['operation']
                doing[motor]['tilt_hs_dur'] = jobs[motor]['tilt_hs_dur']
                doing[motor]['fast_hs_dur'] = jobs[motor]['fast_hs_dur']
                doing[motor]['runs'] = 0
                doing[motor]['id'] = jobs[motor]['id']
                status[motor]['job_id'] = jobs[motor]['id']
                # print('New job for ' + motor + ' loaded')
            if jobs[motor]['run']:
                op = doing[motor]['operation']
                if op == 'closing':
                    if status[motor]['position'] < doing[motor]['target']:
                        status[motor]['running'] = True
                        run[motor] = 1 * dirs[motor]
                        new_position = status[motor]['position'] + 8
                        if new_position > steps[motor]:
                            new_position = steps[motor]
                        status[motor]['position'] = new_position
                    else:
                        status[motor]['running'] = False
                        doing[motor]['operation'] = 'standby'
                        status[motor]['operation'] = 'standby'
                elif op == 'opening':
                    if status[motor]['position'] > doing[motor]['target']:
                        status[motor]['running'] = True
                        run[motor] = -1 * dirs[motor]
                        new_position = status[motor]['position'] - 8
                        if new_position < 0:
                            new_position = 0
                        status[motor]['position'] = new_position
                    else:
                        status[motor]['running'] = False
                        doing[motor]['operation'] = 'standby'
                        status[motor]['operation'] = 'standby'
            else:
                status[motor]['running'] = False
                status[motor]['operation'] = 'standby'
        if run[MOTOR0] == 1:
            if run[MOTOR1] == 1:
                run_both_opp(m0pins, m1pins)
            elif run[MOTOR1] == 0:
                off(m1pins)
                run_ccw(m0pins)
            elif run[MOTOR1] == -1:
                run_both_ccw(m0pins, m1pins)
        elif run[MOTOR0] == 0:
            off(m0pins)
            if run[MOTOR1] == 1:
                run_cw(m1pins)
            elif run[MOTOR1] == 0:
                off(m1pins)
            elif run[MOTOR1] == -1:
                run_ccw(m1pins)
        elif run[MOTOR0] == -1:
            if run[MOTOR1] == 1:
                run_both_cw(m0pins, m1pins)
            elif run[MOTOR1] == 0:
                off(m1pins)
                run_cw(m0pins)
            elif run[MOTOR1] == -1:
                run_both_opp(m1pins, m0pins)

    off(m0pins)
    off(m1pins)
    # print('Stepper thread stopped')
    status['threaded'] = False

# TODO: Check for running operations and cancel them first
# TODO: See if motor calibrated
# TODO: See if lowered (position > -1)
# TODO: Start thread if not stopped
def tilt(motor, target, hs_dur=TILT_HS_DUR):
    if not status['threaded']:
        _thread.start_new_thread(_stepperThread, ())
    if motor == MOTOR0 or motor == MOTOR1:
        jobs[motor]['tilt_hs_dur'] = hs_dur
        jobs[motor]['operation'] = 'tilt'
        jobs[motor]['target'] = target
        if jobs[motor]['id'] >= 1023:
            jobs[motor]['id'] = 0
        else:
            jobs[motor]['id'] += 1
        jobs[motor]['run'] = True
    else:
        raise Exception("No motor specified!")
    
def stop(motor="quit"):
    if motor == "quit":
        jobs["quit"] = True
    elif motor == MOTOR0 or motor == MOTOR1:
        jobs[motor]['run'] = False
    else:
        raise Exception("No motor specified!")