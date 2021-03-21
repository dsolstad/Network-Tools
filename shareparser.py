#!/usr/bin/env python3
##
## Recursevely parses nmap scans (xml) looking for network shares, 
##   discovered with the plugin smb-enum-shares, and presents the result in CSV.
##
## Author: Daniel Solstad (dsolstad.com)
##

import sys

if not sys.version_info[0] == 3:
    print ("Your need to run this with python3")
    sys.exit()

import re
import os
import xml.etree.ElementTree as ET

help = """
shareparser.py <path/to/folder>

Recursevely parses nmap scans (xml) looking for network shares, discovered with the plugin smb-enum-shares, and presents the result in CSV.
"""

if len(sys.argv) != 2:
    print (help)
    sys.exit(1)


rootfolder = sys.argv[1]

# Print CSV header
print ("Share,DNS,Type,Comment,Path,Anonymous access,User,Current user access")

for subdir, dirs, files in os.walk(rootfolder):
    # Iterate through each file
    for file in files:

        filename = os.path.join(subdir, file)
        # Skip non-XML files
        if not filename.endswith('.xml'): continue

        tree = ET.parse(filename)
        root = tree.getroot()

        # Iterate through each host
        for host in root.iter('host'):
        
            # Skip if there are no shares found
            if not host.find(".//hostscript"): continue
            
            # Gather DNS info
            dns = '<none>'
            if host.find(".//hostnames/hostname"):
                dns = host.find(".//hostnames/hostname").attrib['name']
            
            # Fetch the account used from the raw script output
            raw_output = host.find(".//hostscript/script").attrib['output']
            user = re.findall(r'account_used: (\S*)', raw_output)[0]
            
            info = {}
            for table in root.iter('table'):
                info['share'] = table.attrib['key']
                info['dns'] = dns
                info['type'] = host.find(".//elem[@key='Type']").text
                info['comment'] = host.find(".//elem[@key='Comment']").text
                info['path'] = host.find(".//elem[@key='Path']").text
                info['anon'] = host.find(".//elem[@key='Anonymous access']").text
                info['user'] = user
                info['access'] = host.find(".//elem[@key='Current user access']").text
                
                for key, value in info.items():
                    print (value, end='')
                    print (',', end='')
                print ()
