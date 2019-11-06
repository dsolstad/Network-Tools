#!/usr/bin/env python3
##
## Simple segmentation scan
## Author: Daniel Solstad (dsolstad.com)
##
## 1. Get all unique ports from all nmap scans with nmapuniqueports.py. 
##    $ python3 nmapuniqueports.py /path/to/previous/results > ports.txt
##
## 2. Write target subnets in targets.txt (seperated with newlines), then run:
##    cat targets.txt | xargs -I CMD -P 3 python3 nmapsegtest.py CMD
##    This will run three nmap processes in parallel at all times. 
##    Increase/decrease accordingly to your network load.
##
## 3. Move the results to a subfolder named e.g. after the source subnet. Example structure:
##    /segtest/Results/Source_VLAN_101
##    /segtest/Results/Source_VLAN_102
##
## 4. Run $ python3 nmapmerge.py /segtest/Results/Source_VLAN_101 to 
##     view all potential openings from that VLAN.
##

import sys

if not sys.version_info[0] == 3:
    print ("You need to run this with Python 3")
    sys.exit()

import os
import re
import subprocess

target = sys.argv[1]
target = target.replace("\n", "")

if '/' in target:
    results_dir = './Results/' + target.replace('/', '[') + ']/'
else:
    results_dir = './Results/' + target + '/'

if not os.path.exists(results_dir):
    os.makedirs(results_dir)

ports = open('./ports.txt','r').read().replace('\r', '').replace('\n', ',')

cmd = ['nmap', '-sT', target, '-T4', '-n', '-v', '-Pn', '--reason', '-p', ports,
       '--max-retries=1',
       '--max-rtt-timeout=150ms',
       '-oA', results_dir + 'scan']

p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

for line in p.stdout:
    line = line.decode('ascii')
    print (line.rstrip())
