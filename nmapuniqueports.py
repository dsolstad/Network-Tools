#!/usr/bin/env python3
##
## Get unique ports from nmap scans
## Author: Daniel Solstad (dsolstad.com)
##

#!/usr/bin/env python3
 
import sys
import os
 
help = """
nmapunique.py </path/to/scans>
 
This script enumerates and prints out every unique port discovered in nmap scans.
It will search in all subdirectries from the given starting point in the argument.
Note that it will only find ports in files stored in the .nmap format.
"""
 
if len(sys.argv) < 2:
    print (help)
    sys.exit(1)
 
path = sys.argv[1]
 
os.system("grep -Er '^[0-9]{1,6}\/[tcp|udp]' " + path + " | cut -d':' -f2 | cut -d'/' -f1 | sort -n | uniq | tr '\n' ','")
