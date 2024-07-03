#!/usr/bin/env python3
##
## A tool to merge multiple nmap scans into CSV
## Author: Daniel Solstad (dsolstad.com)
##

import sys

if not sys.version_info[0] == 3:
    print ("You need to run this with python3")
    sys.exit()

import os
import re

help = """
nmapmerge.py <path/to/folder>

The script will recursivly find all .nmap files from the target path and print out the merged result in CSV. 
"""

if len(sys.argv) != 2:
    print (help)
    sys.exit(1)

rootfolder = sys.argv[1]
results = []

for subdir, dirs, files in os.walk(rootfolder):
    for file in files:

        filename = os.path.join(subdir, file)
        if not filename.endswith('.nmap'): continue

        for scan in open(filename, 'r').read().split("Nmap scan report"):

            info = {}
            ipaddr = re.findall(r'for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', scan)
            ports = re.findall(r'(\d+)\/(tcp|udp)[ ]+(\w*?)[ ]+([A-Za-z0-9\/\-\?]*)[ ]*?(.*)', scan)
            try:
                for key, val in enumerate(ports):
                    info['ipaddr'] = ipaddr[0]
                    info['port'] = val[0]
                    info['protocol'] = val[1]
                    info['state'] = val[2]
                    info['service'] = val[3]
                    info['version'] = val[4]
                    results.append(dict(info))
            except: pass

try:
    # Print CSV headers
    for item in results[0].keys():
        print(item + ',', end='')

    # Print CSV values
    for x in results:
        print("\n", end='')
        for key, value in x.items():
            print(value, end='')
            print(',', end='')
    print("")
except: pass
