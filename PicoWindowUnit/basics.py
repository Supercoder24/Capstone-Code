from machine import Pin
from time import sleep, ticks_ms, ticks_diff

ain1 = Pin(2,Pin.OUT)
ain2 = Pin(3,Pin.OUT)
ain3 = Pin(4,Pin.OUT)
ain4 = Pin(5,Pin.OUT)

bin1 = Pin(6,Pin.OUT)
bin2 = Pin(7,Pin.OUT)
bin3 = Pin(8,Pin.OUT)
bin4 = Pin(9,Pin.OUT)

astop1 = Pin(10, Pin.IN, Pin.PULL_UP)

# Blink

def blink(sid=0):
    if sid == 0:
        ain1.value(True)
        ain2.value(True)
        ain3.value(True)
        ain4.value(True)
        sleep(1)
        ain1.value(False)
        ain2.value(False)
        ain3.value(False)
        ain4.value(False)
    else:
        bin1.value(True)
        bin2.value(True)
        bin3.value(True)
        bin4.value(True)
        sleep(1)
        bin1.value(False)
        bin2.value(False)
        bin3.value(False)
        bin4.value(False)

sequence = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
half_sequence = [[1, 0, 0, 0], [1,1,0,0], [0, 1, 0, 0], [0,1,1,0], [0, 0, 1, 0], [0,0,1,1], [0, 0, 0, 1], [1,0,0,1]]

on = [0, 1, 2, 3]
cw_off = [3, 0, 1, 2]
ccw_off = [1, 2, 3, 0]

def min_half_step(steps):
    taken = 0
    start = ticks_ms()
    ain1.value(True)
    ain2.value(False)
    ain3.value(False)
    bin1.value(True)
    bin2.value(False)
    bin3.value(False)
    for i in range(int(steps / 8)):
        if astop1.value() == 1:
            break
        ain4.value(False)
        bin4.value(False)
        sleep(0.001)
        ain2.value(True)
        bin2.value(True)
        sleep(0.001)
        ain1.value(False)
        bin1.value(False)
        sleep(0.001)
        ain3.value(True)
        bin3.value(True)
        sleep(0.001)
        ain2.value(False)
        bin2.value(False)
        sleep(0.001)
        ain4.value(True)
        bin4.value(True)
        sleep(0.001)
        ain3.value(False)
        bin3.value(False)
        sleep(0.001)
        ain1.value(True)
        bin1.value(True)
        sleep(0.001)
        taken += 8
    ain4.value(False)
    bin4.value(False)
    ain1.value(False)
    bin1.value(False)
    print('Took ' + str(ticks_diff(ticks_ms(), start)) + ' ms to move ' + str(taken) + ' half steps')

def quick_step(sid, steps, delay=0.005, half=False, ccw=False):
    start = ticks_ms()
    if sid == 0:
        ain1.value(False)
        ain2.value(False)
        ain3.value(False)
        ain4.value(False)
    else:
        bin1.value(False)
        bin2.value(False)
        bin3.value(False)
        bin4.value(False)
    for i in range(steps):
        if half:
            if i % 2 == 0:
                pid = on[int(i/2) % 4]
                if pid == 0:
                    ain1.value(True)
                elif pid == 1:
                    ain2.value(True)
                elif pid == 2:
                    ain3.value(True)
                elif pid == 3:
                    ain4.value(True)
            else:
                pid = 0
                if ccw:
                    pid = ccw_off[int(i/2) % 4]
                else:
                    pid = cw_off[int(i/2) % 4]
                if pid == 0:
                    ain1.value(False)
                elif pid == 1:
                    ain2.value(False)
                elif pid == 2:
                    ain3.value(False)
                elif pid == 3:
                    ain4.value(False)

        #     step = half_sequence[i % len(half_sequence)]
        # else:
        #     step = sequence[i % len(sequence)]
        # if sid == 0:
        #     ain1.value(step[0] == 1)
        #     ain2.value(step[1] == 1)
        #     ain3.value(step[2] == 1)
        #     ain4.value(step[3] == 1)
        # else:
        #     bin1.value(step[0] == 1)
        #     bin2.value(step[1] == 1)
        #     bin3.value(step[2] == 1)
        #     bin4.value(step[3] == 1)
        sleep(delay)
    if sid == 0:
        ain1.value(False)
        ain2.value(False)
        ain3.value(False)
        ain4.value(False)
    else:
        bin1.value(False)
        bin2.value(False)
        bin3.value(False)
        bin4.value(False)
    if half:
        print('Took ' + str(ticks_diff(ticks_ms(), start)) + ' ms to move ' + str(steps) + ' half steps')
    else:
        print('Took ' + str(ticks_diff(ticks_ms(), start)) + ' ms to move ' + str(steps) + ' steps')

def step(sid, steps, delay=0.005, half=False):
    start = ticks_ms()
    if sid == 0:
        ain1.value(False)
        ain2.value(False)
        ain3.value(False)
        ain4.value(False)
    else:
        bin1.value(False)
        bin2.value(False)
        bin3.value(False)
        bin4.value(False)
    for i in range(steps):
        if half:
            step = half_sequence[i % len(half_sequence)]
        else:
            step = sequence[i % len(sequence)]
        if sid == 0:
            ain1.value(step[0] == 1)
            ain2.value(step[1] == 1)
            ain3.value(step[2] == 1)
            ain4.value(step[3] == 1)
        else:
            bin1.value(step[0] == 1)
            bin2.value(step[1] == 1)
            bin3.value(step[2] == 1)
            bin4.value(step[3] == 1)
        sleep(delay)
    if sid == 0:
        ain1.value(False)
        ain2.value(False)
        ain3.value(False)
        ain4.value(False)
    else:
        bin1.value(False)
        bin2.value(False)
        bin3.value(False)
        bin4.value(False)
    if half:
        print('Took ' + str(ticks_diff(ticks_ms(), start)) + ' ms to move ' + str(steps) + ' half steps')
    else:
        print('Took ' + str(ticks_diff(ticks_ms(), start)) + ' ms to move ' + str(steps) + ' steps')
    
def deg2hs(deg):
    return int(deg / 360 * 4096)
def rev2hs(rev):
    return int(rev * 4096)