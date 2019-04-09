#!/usr/bin/env python3
##
## Segmentation test
## Author: Daniel Solstad (dsolstad.com)
##
## cat targets.txt | xargs -I CMD -P 3 python3 segtest.py CMD
##
## Afterwards run python3 nmapmerge.py /path/to/Results to view all potential openings.
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

results_dir = './Results/' + target.replace('/', '[') + ']/'

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
