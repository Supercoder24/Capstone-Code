"""
Automatic file transfer code for centralized multi-controller communication
Designed and implemented by John Cole Brown and Felix Airhart in 2024
"""

# Example data
variables = [["a30","a30","m50","m90","a30","m-2"]]

# Code below
import os
hosts=open("pi_ips",'r').read().split(',')
for host_num in range(len(hosts)):
    file_name = hosts[host_num] + ".txt"
    overwrite = False
    try:
        with open(file_name, 'r') as file:
            overwrite = file.read() != ",".join(variables[host_num])
    except:
        overwrite = True
    if overwrite:
        with open(file_name, 'w') as file:
            file.write(",".join(variables[host_num]))
        os.system('scp "%s" "%s:%s"' % (file_name, hosts[host_num], "~/env/variables.txt"))
