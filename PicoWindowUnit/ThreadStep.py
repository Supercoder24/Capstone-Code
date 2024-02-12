"""
Library for running two stepper motor simultaneously on Core 1 of a Raspberry Pi Pico
Designed and implemented by Felix Airhart in 2024

Configuration:
* configure(m0pins, m1pins, ?tilt_hs_dur, ?fast_hs_dur, ?max_steps)

Functions:
* extend(motor, ?max_steps, ?hs_dur) (hs_dur is seconds between half steps)
* retract(motor, ?max_steps, ?hs_dur)
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
MAX_STEPS = 360000 # maximum steps to try to hit limit switch on each end
TILT_STEPS = 1024 # 4096 half steps per rev / 4 = 90 deg of steps

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

limits = {
    'm0': [Pin(10,Pin.IN,Pin.PULL_UP), # upper limit switch
           Pin(11,Pin.IN,Pin.PULL_UP)], # lower limit switch
    'm1': [Pin(12,Pin.IN,Pin.PULL_UP),
           Pin(13,Pin.IN,Pin.PULL_UP)],
}

def configure(new_m0pins, new_m1pins, new_limitspins, new_tilt_steps):
    global m0pins
    global m1pins
    global limits
    global TILT_STEPS
    m0pins = new_m0pins
    m1pins = new_m1pins
    limits[MOTOR0][0] = new_limitspins[0]
    limits[MOTOR0][1] = new_limitspins[1]
    limits[MOTOR1][0] = new_limitspins[2]
    limits[MOTOR1][1] = new_limitspins[3]
    TILT_STEPS = new_tilt_steps

# Position:
# * -2 all the way up, triggering limit switch
# * -1 in between, no idea where
# * 0 all the way down, but completely open
# * y where 0 < y < TILT_STEPS all the way down, tilted between open and closed
# * x where x = TILT_STEPS all the way down, completely closed, triggering limit switch

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
    print('Motor0 running:\t' + str(status[MOTOR0]['running']) + '\tJob: ' + str(status[MOTOR0]['job_id']) + '\t' + str(status[MOTOR0]['operation']) + '\tPosition: ' + str(status[MOTOR0]['position']) + '\tLimits: ' + str(limits[MOTOR0][0].value()) + ', ' + str(limits[MOTOR0][1].value()))
    print('Motor1 running:\t' + str(status[MOTOR1]['running']) + '\tJob: ' + str(status[MOTOR1]['job_id']) + '\t' + str(status[MOTOR1]['operation']) + '\tPosition: ' + str(status[MOTOR1]['position']) + '\tLimits: ' + str(limits[MOTOR1][0].value()) + ', ' + str(limits[MOTOR1][1].value()))

def stat_feed():
    while True:
        stat()
        utime.sleep(1)

# Operations: 
# * standby (doing nothing)
# * calibrating (lowering to limit switch)
# * extending (lowering to limit switch)
# * retracting (raising to limit switch)
# * opening (tilting away from limit switch)
# * closing (tilting towards limit switch)

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
        'max_steps': MAX_STEPS, # Calibrating
    },
    'm1': {
        'id': 0, # Increments automatically. Resets every 1024
        'run': False, # set True to execute operation
        'operation': 'standby',
        'target': 0, # Tilting
        'tilt_hs_dur': TILT_HS_DUR,
        'fast_hs_dur': FAST_HS_DUR,
        'max_steps': MAX_STEPS, # Calibrating
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

# TODO: Limit switches
# TODO: Choice: variable speeds for tilt and raise -or- consolidate speeds into 1 constant
# TODO: Choice: implement max_steps support -or- remove max_steps
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
            'max_steps': 360000, # Calibrating
            'runs': 0,
        },
        'm1': {
            'id': 0, # Increments automatically. Resets every 1024
            'operation': 'standby',
            'target': 0, # Tilting
            'tilt_hs_dur': 0.001,
            'fast_hs_dur': 0.001,
            'max_steps': 360000, # Calibrating
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
                doing[motor]['max_steps'] = jobs[motor]['max_steps']
                doing[motor]['runs'] = 0
                doing[motor]['id'] = jobs[motor]['id']
                status[motor]['job_id'] = jobs[motor]['id']
                # print('New job for ' + motor + ' loaded')
            if jobs[motor]['run']:
                op = doing[motor]['operation']
                if op == 'extending':
                    if limits[motor][1].value() == 0: # Limit switch not pressed
                        run[motor] = 1
                        status[motor]['running'] = True
                        status[motor]['position'] = -1
                    else:
                        status[motor]['position'] = TILT_STEPS
                        status[motor]['running'] = False
                        doing[motor]['operation'] = 'standby'
                        status[motor]['operation'] = 'standby'
                elif op == 'closing':
                    if limits[motor][1].value() == 0: # Limit switch not pressed
                        if status[motor]['position'] < doing[motor]['target']:
                            status[motor]['running'] = True
                            run[motor] = 1
                            new_position = status[motor]['position'] + 8
                            if new_position > TILT_STEPS:
                                new_position = TILT_STEPS
                            status[motor]['position'] = new_position
                        else:
                            status[motor]['running'] = False
                            doing[motor]['operation'] = 'standby'
                            status[motor]['operation'] = 'standby'
                    else:
                        status[motor]['position'] = TILT_STEPS
                        status[motor]['running'] = False
                        doing[motor]['operation'] = 'standby'
                        status[motor]['operation'] = 'standby'
                    # Maybe notify that ended early
                elif op == 'retracting':
                    if limits[motor][0].value() == 0: # Limit switch not pressed
                        run[motor] = -1
                        status[motor]['running'] = True
                        status[motor]['position'] = -1
                    else:
                        status[motor]['position'] = -2
                        status[motor]['running'] = False
                        doing[motor]['operation'] = 'standby'
                        status[motor]['operation'] = 'standby'
                elif op == 'opening':
                    if status[motor]['position'] > doing[motor]['target']:
                        status[motor]['running'] = True
                        run[motor] = -1
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
    
def retract(motor, max_steps=MAX_STEPS, hs_dur=FAST_HS_DUR):
    if not status['threaded']:
        _thread.start_new_thread(_stepperThread, ())
    if motor == MOTOR0 or motor == MOTOR1:
        jobs[motor]['fast_hs_dur'] = hs_dur
        jobs[motor]['operation'] = 'retracting'
        jobs[motor]['max_steps'] = max_steps
        if jobs[motor]['id'] >= 1023:
            jobs[motor]['id'] = 0
        else:
            jobs[motor]['id'] += 1
        jobs[motor]['run'] = True
    else:
        raise Exception("No motor specified!")
        
def extend(motor, max_steps=MAX_STEPS, hs_dur=FAST_HS_DUR):
    if not status['threaded']:
        _thread.start_new_thread(_stepperThread, ())
    if motor == MOTOR0 or motor == MOTOR1:
        jobs[motor]['fast_hs_dur'] = hs_dur
        jobs[motor]['operation'] = 'extending'
        jobs[motor]['max_steps'] = max_steps
        if jobs[motor]['id'] >= 1023:
            jobs[motor]['id'] = 0
        else:
            jobs[motor]['id'] += 1
        jobs[motor]['run'] = True
    else:
        raise Exception("No motor specified!")