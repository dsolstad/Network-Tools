#!/usr/bin/env python3
##
## Recursively parses nmap scans (xml) looking for network shares (SMB/CIFS/NFS/FTP), 
##   discovered with the plugins smb-enum-shares, smb-ls, nfs-ls and ftp-anon, and presents the result in a merged CSV.
##
## Author: Daniel Solstad (dsolstad.com)
## Version 0.21
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

Recursively parses nmap scans (xml) looking for network shares (SMB/CIFS/NFS/FTP), discovered with the plugins smb-enum-shares and ftp-anon, and presents the result in a merged CSV.
"""

if len(sys.argv) != 2:
    print (help)
    sys.exit(1)


rootfolder = sys.argv[1]

# Print CSV header
print ("ipaddr;dns;type;share;comment;anonymous_access;user_used;authenticated_user_access")

info = []

for subdir, dirs, files in os.walk(rootfolder):
    # Iterate through each file
    for file in files:

        filename = os.path.join(subdir, file)
        # Skip non-XML files
        if not filename.endswith('.xml'): continue

        root = ET.parse(filename).getroot()

        # Iterate through each host
        for host in root.iter('host'):
            
            # Fetch IP address and DNS
            ip = ''
            dns = '<none>'
            try:
                if host.find(".//address").attrib['addr']:
                    ip = host.find(".//address").attrib['addr']
                    
                if host.find(".//hostnames/hostname").attrib['name']:
                    dns = host.find(".//hostnames/hostname").attrib['name']
            except: pass
            

            # Look for FTP services
            # TODO: Consider listing all files/folders on each line.
            for port in host.iter('port'):
                if port.find(".//service").attrib['name'] == 'ftp' and port.find(".//state").attrib['state'] == 'open':
                    res = {'ip':ip, 'dns':dns, 'type':'FTP', 'share':'', 'comment':'', 'anon':'disabled', 'user':'<none>', 'access':''}
                    res['share'] = host.find(".//address").attrib['addr'] + ':' + port.attrib['portid']
                    try:
                        raw = port.find(".//script[@id='ftp-anon']").attrib["output"]
                        if "Anonymous FTP login allowed" in raw:
                            res['anon'] = 'allowed'
                            res['user'] = 'anonymous'
                            res['comment'] = "Port " + str(port.attrib['portid'])
                    except: pass
                    info.append(res)

                # Look for NFS shares (nfs-ls) 
                if port.find(".//script[@id='nfs-ls']"):
                    # Iterate through all the tables
                    for table in port.findall(".//script[@id='nfs-ls']/table[@key='volumes']/table"):

                        share = table.find("elem[@key='volume']")
                        access = table.find("table[@key='info']/elem")
                        
                        # Remove non-access
                        access = access.text.replace('access: ','')
                        access = '/'.join(x for x in access.split(' ') if not x.startswith('No'))

                        res = {'ip':ip, 'dns':dns, 'type':'NFS', 'share':'', 'comment':'', 'anon':'', 'user':'', 'access':''}
                        res['comment'] = "Port " + str(port.attrib['portid'])
                        res['dns'] = dns
                        res['share'] = share.text
                        res['anon'] = access
                        info.append(res)

                        
            # Look for smb-ls output.
            # Sometimes, smb-enum-shares will report READ(/WRITE) access on shares where there is anonymous access, 
            # but it seems like a false positive and you can't even list the folder contents.
            # Here we can use smb-ls that tries to list the directories with anonymous login 
            # to remove these false positives.
            smb_ls = []
            if host.find(".//hostscript/script[@id='smb-ls']"):
                volumes = host.find(".//hostscript/script[@id='smb-ls']/table[@key='volumes']")
                for elem in volumes.iter("elem"):
                    try:
                        if elem.attrib['key'] == 'volume':
                            smb_ls.append(elem.text.split('\\').pop())
                    except: pass

            # Look for smb-enum-shares output
            if host.find(".//hostscript/script[@id='smb-enum-shares']"):
                smb_enum_shares = host.find(".//hostscript/script[@id='smb-enum-shares']")
                # Fetch the account used from the raw script output
                try:
                    raw = smb_enum_shares.attrib['output']
                    user = re.findall(r'account_used: (\S*)', raw)[0]
                except: pass
                
                for table in smb_enum_shares.iter('table'):
                    res = {'ip':ip, 'dns':dns, 'type':'SMB/CIFS', 'share':'', 'comment':'', 'anon':'', 'user':'' ,'access':''}
                    try:
                        res['share'] = table.attrib['key'].split('\\').pop()
                        res['dns'] = dns
                        res['comment'] = table.find(".//elem[@key='Comment']").text
                        res['anon'] = table.find(".//elem[@key='Anonymous access']").text
                        res['user'] = user
                        res['access'] = table.find(".//elem[@key='Current user access']").text
                    except: pass
                    
                    # Setting anon access and auth access to <none> if smb-ls didn't get to list the file contents
                    if res['share'] not in smb_ls:
                        res['anon'] = '<none>'
                        res['access'] = '<none>'
                        
                    info.append(res)




# Print out results
for obj in info:                    
    for key, value in obj.items():
        print (value, end='')
        print (';', end='')
    print ()
        
