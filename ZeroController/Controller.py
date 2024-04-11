import time
import json
from Talker import Talker

connected = 8 # Window units, not picos
found = 0
ports = []
pis = []
unit_index = []

# Default config for 8 window units
config = {
    "connected": 8,
    "steps": [1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024],
    "dirs": [1, 1, 1, 1, 1, 1, 1, 1]
}
# {
#     "connected": 8, # <int> # of window units connected
#     "steps": [1024, 1024, 1024, 1024, 1024, 1024, 1024, 1024], # [<int>] # of steps each window unit can turn
#     "dirs": [1, 1, 1, 1, 1, 1, 1, 1] # [1 or -1] direction multipler # TODO: 1 = CW or CCW ?
# }

try:
    with open('config.json', 'r') as file:
        config = json.loads(file.read())
except Exception as e:
    print("Couldn't read config!")
    print()
    print(e)

connected = config['connected']

class Pi:
    def __init__(self, port):
        self.port = port
        talker = Talker(self.port)
        talker.send('led = Pin(25, Pin.OUT);s = led.value')
        talker.close()

    def cmd(self, command, no_receive=False):
        try:
            talker = Talker(self.port)
            talker.send('s(True)')
            talker.send(command)
            received = ''
            if not no_receive:
                received = talker.receive()
            talker.send('s(False)')
            talker.close()
            # if not no_receive:
            return received #TODO: INDENT AND UNCOMMENT IF
        except Exception as e:
            print('Failed to connect! {}'.format(e))
            return ':('
    

while found < connected:
    time.sleep(0.5)
    for i in range(64):
        try:
            if i not in ports:
                talker = Talker(i)
                talker.close()
                ports.append(i)
                pis.append(Pi(i))
                found += 2
                for j in range(2):
                    unit_index.append([i,j])
                    print('Added window unit %s' % len(unit_index))
                    print(unit_index)
                print('Connected pico with 2 units')
                break
        except Exception as e:
            if str(e)[0:2] != '[E':
                print(e)

print('Connected to all!')

# TODO: NOTIFY/RECONNECT IF DISCONNECTED

variables = []

while True:
    new_data = False
    with open('variables.txt', 'r') as file:
        data = file.read()
        if data != ','.join(variables):
            print('New data!')
            variables = data.split(',')
            print(variables)
            new_data = True

    # TODO: Only send changes if necessary
    for i in range(len(variables)):
        instruction = variables[i]
        mode = instruction[0:1]
        value = instruction[1:]
        pi = unit_index[i][0]
        motor = unit_index[i][1]
        if mode == 'a':
            # TODO: AUTOMATIC OPERATION
            pass
        elif mode == 'm':
            print('Unit ' + str(i) + ': ' + pis[pi].cmd('pos("m' + str(motor) + '",' + value + ')'))

    with open('config.json', 'r') as file:
        next_config = file.read()
        for i in range(len(config['steps'])):
            pi = unit_index[i][0]
            motor = unit_index[i][1]
            if next_config['steps'][i] != config['steps'][i]:
                config['steps'][i] = next_config['steps'][i]
                pis[pi].cmd('cfg_steps("m' + str(motor) + '",' + str(next_config['steps'][i]) + ')')
                print('Updated Config Steps')
            if next_config['dirs'][i] != config['dirs'][i]:
                config['dirs'][i] = next_config['dirs'][i]
                pis[pi].cmd('cfg_dir("m' + str(motor) + '",' + str(next_config['dirs'][i]) + ')') 
                print('Updated Config Directions')
