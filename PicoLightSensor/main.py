from machine import Pin, ADC
ls0 = ADC(26)
ls1 = ADC(27)

def typ():
    return 'ls' # Light Sensor
