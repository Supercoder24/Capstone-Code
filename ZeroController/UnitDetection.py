import time
from Talker import Talker

connected = 2
found = 0
ports = []
pis = []
unit_index = []

class Pi:
    connected = [False, False]

    def __init__(self, port, found_units):
        self.port = port
        if self.cmd('stat("m0l")', True) < '1': # If not installed, will be 2 TODO: REMOVE True here
            self.connected[0] = True
        if self.cmd('stat("m1l")', True) < '1': # If not installed, will be 2 TODO: REMOVE True here
            self.connected[1] = True

    def cmd(self, command, no_receive=False):
        try:
            talker = Talker(self.port)
            talker.send(command)
            received = ''
            if not no_receive:
                received = talker.receive()
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
                pis.append(Pi(i, len(unit_index)))
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

                pis[found].cmd('led = Pin(25, Pin.OUT)',True)
                pis[found].cmd('led.value(True)',True)
                break
        except:
            pass

print('Connected to all!')
