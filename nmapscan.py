#!/usr/bin/env python3
##
## A wrapper around nmap
## Author: Daniel Solstad (dsolstad.com)
##

import sys

if not sys.version_info[0] == 3:
    print ("You need to run this with Python 3")
    sys.exit()

import sys
import os
import re
import subprocess
import time
import math
from termcolor import colored

help = """
nmapscan.py <target> <src interface> [<path/to/ports.txt>]

The <target> parameter can be a single host, range or a network with appending netmask (CIDR)

The optional ports file needs to contain TCP ports on line 1 and UDP ports on line 2 (comma separated).
If no ports file is present it will scan all 1 to 65535 tcp and top 100 udp ports.

Example:
nmapscan.py 192.168.1.0/24 eth1.101 /home/ports.txt
nmapscan.py 192.168.1.1-5 eth1.101 /home/ports.txt

ports.txt: 
80,443,445,8080
67,68,69
"""

if len(sys.argv) < 3:
    print (help)
    sys.exit(1)

target = sys.argv[1]
interface = sys.argv[2]

# UDP top 100 ports
udp_ports = "7,9,17,19,49,53,67-69,80,88,111,120,123,135-139,158,161-162,177,427,443,"
udp_ports += "445,497,500,514-515,518,520,593,623,626,631,996-999,1022-1023,1025-1030,"
udp_ports += "1433-1434,1645-1646,1701,1718-1719,1812-1813,1900,2000,2048-2049,2222-2223,"
udp_ports += "3283,3456,3703,4444,4500,5000,5060,5353,5632,9200,10000,17185,20031,30718,"
udp_ports += "31337,32768-32769,32771,32815,33281,49152-49154,49156,49181-49182,49185-49186,"
udp_ports += "49188,49190-49194,49200-49201,65024"

tcp_ports = '1-65535'

# If the optional file input parameter is given
if len(sys.argv) == 4:
    try:
        ports_from_file = open(sys.argv[3], 'r').read().replace('\r', '')
    except:
        print (colored('[+] Cannot open file for reading. Aborting.', 'red'))
        sys.exit(1)

    print ('[+] Reading ports from ' + sys.argv[3])
    match = re.match('(.*?)\n(.*)', ports_from_file)

    if match:
        tcp_ports = match.group(1)
        udp_ports = match.group(2)
    else:
        print (colored('[+] Wrong format in file. Aborting.', 'red'))
        sys.exit(1)
else:
    print ('[+] No input file with ports given. Using defaults.')

ports = '-pT:' + tcp_ports + ',U:' + udp_ports

## Creating the output folder
if target.find('/') != -1:
    results_dir = './Results/' + target.replace('/', '[') + ']/'
else:
    results_dir = './Results/'

if not os.path.exists(results_dir):
    os.makedirs(results_dir)

## Host discovery
## We need to do host discovery first to be able to get 
## the result from the port scan in different output files.

print ('[+] Initiating host discovery')
result = subprocess.check_output(['nmap', '-sn', target, '-e', interface])
# Extract all valid IP addresses
hosts = re.findall(b'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', result)
# Convert the IP addresses to strings from byte-objects
hosts = [s.decode('ascii') for s in hosts] 

if len(hosts) > 0:
    print (colored('[+] Found the following hosts:', 'green'))
    print ("\n".join(hosts))
    print ('[+] Writing result to ' + results_dir + 'host_discovery.txt')
    with open(results_dir + 'host_discovery.txt' , 'w') as out:
        out.write("\n".join(hosts))
else:
    print (colored('[+] Found zero hosts. Aborting.', 'red'))
    sys.exit()

## Port scan

print ('----------------------------------------')

for host in hosts:

    # Creating a folder for the current host
    if not os.path.exists(results_dir + host):
        os.makedirs(results_dir + host)

    print ('[+] Scanning ' + host)
    print ('[+] Storing result in ' + results_dir + host + '/')

    cmd = ['nmap', '-sUTV', host, '-T4', '-O', '-n', '-v', '-Pn', '--reason',
           ports,
           '--stats-every', '5s',
           '-e', interface,
           '-oA', results_dir + host + '/' + host]


    # Debug - Prints out the full nmap command
    # print (" ".join(cmd))

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    
    host_complete = False
    scantype = ''

    while host_complete is False:
        #time.sleep(0.5)
        for line in p.stdout:
            line = line.decode('ascii')
            # Debug - Prints out output from nmap
            # print (line.rstrip())

            match = re.search(r'Initiating (.*?) at', line)
            #print("MATCH",match.group(1))

            if match:
                scantype = match.group(1)
                print ('[+] Initiated ' + scantype)

            percent = re.search('About (.*?)%', line)
            if percent:
                #print (match.group(1))
                curr = math.ceil(float(percent.group(1)) / 2) 
                print ('[' + (colored('X', 'yellow') * curr) + (" " * (50-curr)) + ']', end="\r")

            if line.find('Completed ' + scantype) != -1:
                print ('[' + (colored('X', 'yellow') * 50) +']', end="\r")
                print (colored('\n[+] ' + scantype + ' completed', 'green'))

            # Checking if the scanning of the host is complete 
            match = re.search('Nmap done: 1 IP address', line)
            if match:
                print (colored('[+] Scanning of ' + host + ' completed', 'green'))
                host_complete = True
            else:
                sys.stdout.flush()
                break


