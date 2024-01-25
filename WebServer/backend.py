"""
Automatic file transfer code for centralized multi-controller communication
Designed and implemented by John Cole Brown and Felix Airhart in 2024
"""

file_path = 'variables/'

cache = {}

import os
import subprocess

def ping(host):
    return subprocess.run(args=['ping', '-c', '1', '-w1', host], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

# Loop this
while True:
    hosts = []
    with open(file_path + "pi_ips",'r') as file:
        hosts = file.read().split(',')
        if hosts == ['']:
            hosts = []
    for host in cache:
        if host not in hosts:
            del cache[host]
    for host in hosts:
        file_name = host + ".txt"
        new_data = host not in cache
        if not new_data:
            try:
                with open(file_path + file_name, 'r') as file:
                    new_data = file.read() != cache[host]
            except:
                new_data = False
        if new_data:
            with open(file_path + file_name, 'r') as file:
                cache[host] = file.read()
            if ping(host):
                os.system('scp "%s" "%s:%s"' % (file_path + file_name, host, "~/env/variables.txt"))
            else:
                print('Host: ' + host + ' is not accessible!')