#!/usr/bin/env python3
##
## Simple segmentation scan
## Author: Daniel Solstad (dsolstad.com)
##
## Important! Always start slower and then adjust the speed according to what the target network can handle. This can potentially bring a complete network down.
##
## 1. Choose tcp or udp and ports
##    By default, the script scans all 65k tcp ports. Change cmd_tcp to cmd_udp in the Popen function to scan UDP instead.
##    You can speed up the scan by only scanning unique ports previously seen in the same network with the following command:
##    $ grep -Er '^[0-9]{1,6}\/[tcp|udp]' results/ | grep open | cut -d':' -f2 | cut -d'/' -f1 | sort -n | uniq | tr '\n' ',' > ports.txt
##
## 2. Add targets and start scan
##    Write target subnets in targets.txt (nmap syntax), seperated with newlines, then run:
##    cat targets.txt | xargs -I CMD -P 1 python3 nmapsegtest.py CMD
##    This will run one nmap processes for each target consecutively, but can be increased by adjusting the -P argument, if the target network can handle it.
##    Scanning multiple single hosts will usually benefit more by running multiple nmap instances, 
##      since nmap already does a good job optimizing when scanning a whole subnet.
##    This script use full connect scan (-sT) to be more friendly towards firewalls, so that they don't keep the connections open.
##
## 3. Process results
##    Move the results to a subfolder named e.g. after the source subnet. Example structure:
##    ./segtest/results/Source_VLAN_101
##    ./segtest/results/Source_VLAN_102
##
## 4. View results
##    Run $ python3 nmapmerge.py /segtest/results/Source_VLAN_101 to view all potential openings from that VLAN.
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
    print ("[+] Skipping commented out line: " + target)
    sys.exit()
    
if '/' in target:
    results_dir = './results/' + target.replace('/', '[') + ']/'
else:
    results_dir = './results/' + target + '/'

if os.path.exists(results_dir):
    print ("[+] Skipping already scanned: " + target)
    sys.exit()
else:
    os.makedirs(results_dir)

ports = '1-65535'
if os.path.exists('./ports.txt'):
    ports = open('./ports.txt','r').read().replace('\r', '').replace('\n', ',')

# Be very careful and adjust the min-rate according to the target network.
cmd_tcp = ['nmap', '-sT', target, '-T4', '-n', '-v', '-Pn', '--reason', '-p', ports,
       '--max-retries=1',
       '--max-scan-delay=1',
       '--min-rate=1000',
       '--max-rtt-timeout=200ms',
       '--initial-rtt-timeout=200ms',
       '-oA', results_dir + 'scan']

# We can't scan that fast against UDP ports or the results will be very unaccurate.
# Consider adding version scan (-sUV) for more accurate results at the cost of speed.
cmd_udp = ['nmap', '-sU', target, '-T3', '-n', '-v', '-Pn', '--reason', '--top-ports', '100',
       '-oA', results_dir + 'scan']

print ("[+] Starting scan against: " + target)
p = subprocess.Popen(cmd_tcp, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

for line in p.stdout:
    line = line.decode('ascii')
    print (line.rstrip())
