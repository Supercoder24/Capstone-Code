import time
import json
from Talker import Talker

connected = 4 # Window units, not picos
found = 0
ports = []
pis = []
unit_index = [[-1,-1],[-1,-1],[-1,-1],[-1,-1]] # Length = connected
light_found = False
light_sensor = -1
levels = [0,0]
THRESHHOLD = 5
debug = False

config = {
    "connected": 4,
    "steps": [1024, 1024, 1024, 1024],
    "dirs": [1, 1, 1, 1],
    "ls_min": 1400,
    "ls_max": 300
}
# {
#     "connected": 8, # <int> # of window units connected
#     "steps": [1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024], # [<int>] # of steps each window unit can turn
#     "dirs": [1, 1, 1, 1, 1, 1, 1, 1] # [1 or -1] direction multipler # TODO: 1 = CW or CCW ?
# }

# try:
#     with open('config.json', 'r') as file:
#         config = json.loads(file.read())
# except Exception as e:
#     print("Couldn't read config!")
#     print()
#     print(e)

connected = config['connected']

class Pi:
    def __init__(self, port):
        self.port = port
        while True:
            try:
                talker = Talker(self.port)
                talker.send('led = Pin(25, Pin.OUT);s = led.value')
                # print(talker.receive())
                talker.close()
                break
            except Exception as e:
                print('Failed to initialize! {}'.format(e))
        
        # print('found and initting')
        typ = self.cmd('typ()')
        self.typ = typ
        print('Type: ', typ)

    def cmd(self, command, no_receive=False):
        try:
            talker = Talker(self.port)
            received = ''
            try:
                talker.send('s(True)')
                talker.send(command)
                received = ''
                if not no_receive:
                    received = talker.receive()
                    if debug:
                        last_received = received
                        while last_received != '>>>':
                            print('got: ' + last_received)
                            last_received = talker.receive()
                talker.send('s(False)')
                # if not no_receive:
                # return received #TODO: INDENT AND UNCOMMENT IF
            except Exception as e:
                print('Failed to send! {}'.format(e))
            talker.close()
            return received
        except Exception as e:
            print('Failed to connect! {}'.format(e))
            return ':('
    
x = "'wu0'"

while found < connected or not light_found:
    # time.sleep(0.5)
    for i in range(64):
        try:
            if i not in ports:
                talker = Talker(i)
                talker.close()
                ports.append(i)
                new_pi = Pi(i)
                pis.append(new_pi)
                if (new_pi.typ[0:3] == "'wu"): # Window Unit
                    found += 2
                    offset = int(new_pi.typ[3]) * 2
                    for j in range(2):
                        unit_index[offset + j] = [len(pis) - 1,j]
                        print('Added window unit %s' % (offset + j))
                        print(unit_index)
                    print('Connected pico with 2 units')
                elif (new_pi.typ == "'ls'"): # Light Sensor
                    light_found = True
                    light_sensor = len(pis) - 1
                    print('Connected pico with light sensor')
                else:
                    print('Connected unknown pico')
                break
        except Exception as e:
            if str(e)[0:2] != '[E':
                print(e)

print('Connected to all!')

# TODO: NOTIFY/RECONNECT IF DISCONNECTED

variables = []
t = 0

while True:
    try:
        levels[0] = (int(pis[light_sensor].cmd('ls0.read_u16()')) - config['ls_min']) / (config['ls_max']-config['ls_min']) * 100
        levels[1] = (int(pis[light_sensor].cmd('ls1.read_u16()')) - config['ls_min']) / (config['ls_max']-config['ls_min']) * 100
        if debug:
            print('LEVELS: ' + str(levels[0]) + ', ' + str(levels[1]))
        desired = [_/(len(variables)-1)*levels[0]+(1-_/(len(variables)-1))*levels[1] for _ in range(len(variables))]
        new_data = False
        with open('variables.txt', 'r') as file:
            data = file.read()
            if data != ','.join(variables):
                print('New data!')
                variables = data.split(',')
                print(variables)
                new_data = True
        changes = [-1 for _ in range(len(variables))]
        # print(changes)

        # TODO: Only send changes if necessary
        for i in range(len(variables)):
            instruction = variables[i]
            mode = instruction[0:1]
            value = instruction[1:] if i < len(variables) else instruction[1:-1]
            # print('val: ' + value)
            pi = unit_index[i][0]
            motor = unit_index[i][1]
            # print(i)
            # print(len(changes))
            # print()
            if mode == 'a':
                num_blinds = len(variables)
                bias = i/(num_blinds-1)
                light_value = bias*levels[0]+(1-bias)*levels[1]
                changes[i] = desired[i]+(light_value-desired[i])/2 if light_value-THRESHHOLD>desired[i] or light_value+THRESHHOLD<desired[i] else -1
                # TODO: AUTOMATIC OPERATION
                # Use levels[0] 0-100 left, levels[1] 0-100 right, i = index of window unit (0 on left)
                #value = 0-100
                #print('Unit ' + str(i) + ': ' + pis[pi].cmd('pos("m' + str(motor) + '",' + value + ')'))
            elif mode == 'm':
                changes[i] = value
                #print('Unit ' + str(i) + ': ' + pis[pi].cmd('pos("m' + str(motor) + '",' + value + ')'))
        if debug:
            print('MOVING: ' + str(changes))
        for _ in range(len(changes)):
            # if changes[_] != -1:
            if debug:
                print('passing in ' + str(unit_index[_][1]) + ' and ' + str(changes[_]))
            stat = pis[unit_index[_][0]].cmd('pos("m' + str(unit_index[_][1]) + '",' + str(changes[_]) + ')')
            if t > -1:
                t = 0
                print('Unit ' + str(_) + ': ' + stat)
            else:
                t += 1
    except KeyboardInterrupt:
        print('stopped')
        break
    except Exception as e:
        print('Error in main loop! {}'.format(e))

    # with open('config.json', 'r') as file:
    #     next_config = json.loads(file.read())
    #     for i in range(len(config['steps'])):
    #         pi = unit_index[i][0]
    #         motor = unit_index[i][1]
    #         if next_config['steps'][i] != config['steps'][i]:
    #             config['steps'][i] = next_config['steps'][i]
    #             pis[pi].cmd('cfg_steps("m' + str(motor) + '",' + str(next_config['steps'][i]) + ')')
    #             print('Updated Config Steps')
    #         if next_config['dirs'][i] != config['dirs'][i]:
    #             config['dirs'][i] = next_config['dirs'][i]
    #             pis[pi].cmd('cfg_dir("m' + str(motor) + '",' + str(next_config['dirs'][i]) + ')') 
    #             print('Updated Config Directions')
