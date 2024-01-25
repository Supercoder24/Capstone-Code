import time
from Talker import Talker

connected = 2
found = 0
ports = []
pis = []
unit_index = []

class Pi:
    def __init__(self, port):
        self.port = port
        self.connected = [False, False]
        talker = Talker(self.port)
        talker.send('led = Pin(25, Pin.OUT);s = led.value')
        talker.close()
        if int(self.cmd('stat("m0l")')) <= 1: # If not installed, will be 2 TODO: REMOVE True here
            self.connected[0] = True
        if int(self.cmd('stat("m1l")')) <= 1: # If not installed, will be 2 TODO: REMOVE True here
            self.connected[1] = True

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
                found += 1
                pis.append(Pi(i))
                units = pis[i].connected
                num = 0
                if units[0]:
                    unit_index.append([i,0])
                    print('Added window unit %s' % len(unit_index))
                    print(unit_index)
                    num += 1
                if units[1]:
                    unit_index.append([i,1])
                    print('Added window unit %s' % len(unit_index))
                    print(unit_index)
                    num += 1
                print('Connected pico with %s units' % num)

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

    time.sleep(1)
