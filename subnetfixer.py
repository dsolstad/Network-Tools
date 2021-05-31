#!/usr/bin/env python3
##
## Converts a list of verious length subnets into the same prefix lengths, while also removing duplicates.
## Input file should contain a subnet on each line.
##
## Author: Daniel Solstad (dsolstad.com)
##
## python3 subnetfixer.py <path/to/file.txt> <subnet prefix>
## python3 subnetfixer.py input.txt 24
##

import ipaddress
import sys

subs = []
uniq = {}

for line in open(sys.argv[1], 'r').read().split("\n"):
    subs.append(list(ipaddress.ip_network(line).subnets(new_prefix=int(sys.argv[2]))))

for sub in subs:
    for x in sub:
        uniq[x] = 1

for k, v in uniq.items():
    print (k)
