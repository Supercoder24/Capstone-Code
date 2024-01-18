"""
Automatic file change detection code for centralized multi-controller communication
Designed and implemented by John Cole Brown and Felix Airhart in 2024
"""

from time import sleep

variables = []

while True:
    with open('variables.txt', 'r') as file:
        data = file.read()
        if data != ','.join(variables):
            print('New data!')
            variables = data.split(',')
            print(variables)
    sleep(1)