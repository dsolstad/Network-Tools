#!/usr/bin/env python3
##
## Simple segmentation scan
## Author: Daniel Solstad (dsolstad.com)
##
## 1. Chose ports
##    Add '-p-' as a parameter to scan all 65k ports (uncomment ports variable),
##    or, to speed up the test, get all unique ports from previous nmap scans with:
##    $ grep -Er '^[0-9]{1,6}\/[tcp|udp]' Results/ | grep open | cut -d':' -f2 | cut -d'/' -f1 | sort -n | uniq | tr '\n' ',' > ports.txt
##
## 2. Add targets and start scan
##    Write target subnets in targets.txt (nmap syntax), seperated with newlines, then run:
##    cat targets.txt | xargs -I CMD -P 3 python3 nmapsegtest.py CMD
##    This will run three nmap processes in parallel at all times. Increase/decrease -P accordingly to your network load.
##    You can further add --min-rate=x to the nmap command to speed it up further, but use with caution. Try e.g. with 1000 first.
##
## 3. Process results
##    Move the results to a subfolder named e.g. after the source subnet. Example structure:
##    /segtest/Results/Source_VLAN_101
##    /segtest/Results/Source_VLAN_102
##
## 4. View results
##    Run $ python3 nmapmerge.py /segtest/Results/Source_VLAN_101 to view all potential openings from that VLAN.
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

if '#' in target:
    print ("Skipping commented out line: " + target)
    sys.exit()
    
if '/' in target:
    results_dir = './Results/' + target.replace('/', '[') + ']/'
else:
    results_dir = './Results/' + target + '/'

if os.path.exists(results_dir):
    print ("Skipping - already scanned: " + target)
    sys.exit()
else:
    os.makedirs(results_dir)

ports = open('./ports.txt','r').read().replace('\r', '').replace('\n', ',')

cmd = ['nmap', '-sT', target, '-T4', '-n', '-v', '-Pn', '--reason', '-p', ports,
       '--max-retries=1',
       '--max-scan-delay=1',
       '--max-rtt-timeout=200ms',
       '--initial-rtt-timeout=200ms',
       '-oA', results_dir + 'scan']

print ("Starting scan against: " + target)
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

for line in p.stdout:
    line = line.decode('ascii')
    print (line.rstrip())
