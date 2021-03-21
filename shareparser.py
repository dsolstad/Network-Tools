#!/usr/bin/env python3
##
## Recursevely parses nmap scans (xml) looking for network shares (SMB/CIFS/FTP), 
##   discovered with the plugins smb-enum-shares and ftp-anon, and presents the result in CSV.
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

Recursevely parses nmap scans (xml) looking for network shares (SMB/CIFS/FTP), discovered with the plugins smb-enum-shares and ftp-anon, and presents the result in CSV.
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

        root = ET.parse(filename).getroot()

        # Iterate through each host
        for host in root.iter('host'):
            
            # Fetch DNS info
            dns = '<none>'
            try:
                if host.find(".//hostnames/hostname").attrib['name']:
                    dns = host.find(".//hostnames/hostname").attrib['name']
            except: pass
            
            # Look for FTP services
            # TODO: Consider listing all files/folders on each line.
            for port in host.iter('port'):
                if port.find(".//service").attrib['name'] == 'ftp':
                    info = {}
                    info['share'] = host.find(".//address").attrib['addr'] + ':' + port.attrib['portid']
                    info['dns'] = dns
                    info['type'] = 'FTP'
                    info['comment'] = ''
                    info['path'] = ''
                    info['anon'] = 'disabled'
                    info['user'] = '<none>'
                    info['access'] = ''
                    try:
                        raw = port.find(".//script[@id='ftp-anon']").attrib["output"]
                        if "Anonymous FTP login allowed" in raw:
                            info['anon'] = 'allowed'
                            info['user'] = 'anonymous'
                    except: pass

                    for key, value in info.items():
                        print (value, end='')
                        print (',', end='')
                    print ()


            # Look for smb-enum-shares output
            if host.find(".//hostscript"):
            
                # Fetch the account used from the raw script output
                raw = host.find(".//hostscript/script").attrib['output']
                user = re.findall(r'account_used: (\S*)', raw)[0]
                
                info = {}
                for table in host.iter('table'):
                    info['share'] = table.attrib['key']
                    info['dns'] = dns
                    #info['type'] = host.find(".//elem[@key='Type']").text
                    info['type'] = 'SMB/CIFS'
                    info['comment'] = host.find(".//elem[@key='Comment']").text
                    info['path'] = host.find(".//elem[@key='Path']").text
                    info['anon'] = host.find(".//elem[@key='Anonymous access']").text
                    info['user'] = user
                    info['access'] = host.find(".//elem[@key='Current user access']").text
                    
                    for key, value in info.items():
                        print (value, end='')
                        print (',', end='')
                    print ()
        
 
