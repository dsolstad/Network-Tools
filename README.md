### Table of Contents

[Merge multiple nmap scans into one CSV](https://github.com/dsolstad/Network-Tools#Merge-multiple-nmap-scans-into-one-CSV)  
[Get unique open ports from nmap scans](https://github.com/dsolstad/Network-Tools#Get-unique-open-ports-from-nmap-scans)  
[Resolve all hostnames from a list](https://github.com/dsolstad/Network-Tools#Resolve-all-hostnames-from-a-list)  
[Network segmentation testing](https://github.com/dsolstad/Network-Tools#Network-segmentation-testing)  
[Parse network shares into CSV](https://github.com/dsolstad/Network-Tools#Parse-network-shares-into-CSV)  
[Convert subnets to a given length](https://github.com/dsolstad/Network-Tools#convert-subnets-to-a-given-length)  
[Setup VLAN interfaces](https://github.com/dsolstad/Network-Tools#Setup-VLAN-interfaces)  

# Merge multiple nmap scans into one CSV
The script recursively goes through the given folder to find all .nmap files and presents a combined CSV of the results.  
Syntax:
```
$ nmapmerge.py <path/to/folder>
```
Example:
```
root@kali:~# python3 nmapmerge.py results/
ipaddr,port,protocol,state,service,version,
192.168.1.254,80,tcp,filtered,http,,
192.168.1.254,443,tcp,filtered,https,,
192.168.1.254,445,tcp,filtered,microsoft-ds,,
192.168.1.254,8080,tcp,filtered,http-proxy,,
192.168.1.254,137,udp,open|filtered,netbios-ns,,
192.168.1.254,138,udp,open|filtered,netbios-dgm,,
192.168.1.254,139,udp,open|filtered,netbios-ssn,,
192.168.1.2,80,tcp,open,http,,
192.168.1.2,443,tcp,closed,https,,
192.168.1.2,445,tcp,closed,microsoft-ds,,
192.168.1.2,8080,tcp,closed,http-proxy,,
192.168.1.2,137,udp,open|filtered,netbios-ns,,
192.168.1.2,138,udp,open|filtered,netbios-dgm,,
192.168.1.2,139,udp,open|filtered,netbios-ssn,,
root@kali:~# 
```
Pro tip: Send the result to grep to filter out only open/non-filtered ports:
```
python3 nmapmerge.py results/ | grep open | grep -v filtered
```

# Get unique open ports from nmap scans
Recursively goes through the given folder (e.g. ./results), parses all the files and presents a list of unique ports open. Works for .nmap files.
```
root@kali:~# grep -Er '^[0-9]{1,6}\/[tcp|udp]' results/ | grep open | cut -d':' -f2 | cut -d'/' -f1 | sort -n -u | tr '\n' ','
21,22,23,25,53,80,81,88,89,111,135,139,161,389,427,443,445
root@kali:~# 
```
  
# Get unique IP-addresses from nmap scans
Recursively goes through the given folder (e.g. ./results), parses all the files and presents a list of unique IP addresses. Works best for .gnmap files.
```
root@kali:~# grep -Eorh "([0-9]{1,3}\.){3}[0-9]{1,3}.*Status: Up" Results/ | cut -d' ' -f1 | sort -u
192.168.0.1
192.168.0.2
192.168.0.3
root@kali:~# 
```

# Resolve all hostnames from a list
Returns a list of hostname,ip-addr pairs from a list of hostnames, separated by newlines, in hostnames.txt.
```
root@kali:~# cat hostnames.txt
dns.google.com
google.com
root@kali:~# for h in $(cat ./hostnames.txt); do printf "$h,%s\\n" $(dig +search +short "$h"); done
8.8.4.4,dns.google.com
142.250.74.46,google.com
```

# Network segmentation testing

When doing a blind network scan, where every host is reported to be alive and all ports filtered, a large network scan will take forever to complete. This script runs nmap with optimized and tweaked settings. Please read all the comments in the top section of the script before running.  
Syntax:
```
$ python3 nmapsegtest.py <target network>
```
Pro tip: You can use xargs to do multiple Nmap scans in parallel. Just be sure to find the right number for your network, before you start to lose accuracy. The targets.txt can contain any number of subnets/hosts (separated by newlines). The following command will only run three Nmap processes simultaneously at any given time until the all the targets are scanned.
  
```
$ cat targets.txt | xargs -I CMD -P 3 python3 nmapsegtest.py CMD
```

# Parse network shares into CSV
Recursively parses nmap scans (xml) looking for network shares (SMB/CIFS/NFS/FTP), discovered with the plugins smb-enum-shares, smb-ls, ftp-anon and nfs-ls, and presents the result in a merged CSV. It will also show permissions for each share, and show where no authentication is required.
  
Example of nmap scan to run first:
```
nmap -sT -sU -p U:137,T:21,111,137,139,445 --script smb-enum-shares,smb-ls,ftp-anon,nfs-ls --script-args smbdomain=<domain>,smbusername=<user>,smbpassword=<pw> <target> -oA scan
```
Note: There is a bug in smb.lua which makes the smb-enum-shares plugin throw away all the discovered shares on a host if one of the shares failed. A fix for this is documented here: https://github.com/nmap/nmap/pull/2277/commits/135bd34422b0942c1713540638c59c46156f1c46
  
Protip: You can run an nmap instance for each target to get the output for each subnet in a new file instead. This way, if your scan gets interrupted, you have more control and can easier continue the scan later. This can for example be done like the following.  
  
Bash:
```bash
cat targets.txt | while read t; do nmap -sT -sU -p U:137,T:21,111,137,139,445 --script smb-enum-shares,smb-ls,ftp-anon,nfs-ls --script-args smbdomain=<domain>,smbusername=<user>,smbpassword=<pw> $t -oA $(echo $t | tr '/', '_')
```
Powershell:
```powershell
foreach ($t in (Get-Content ".\targets.txt")) { if ((Test-Path ($t -replace '/','_')) -eq $False) { nmap -sT -sU -p U:137,T:21,111,137,139,445 --script smb-enum-shares,smb-ls,ftp-anon,nfs-ls --script-args smbdomain=<domain>,smbusername=<user>,smbpassword=<pw> $t -oA ($t -replace '/','_') }}
```
Where targets.txt can look like this:
```
192.168.1.0/24
192.168.2.0/24
192.168.3.0/24
```
Shareparser Syntax:
```
$ python3 shareparser.py <path/to/folder>
```

Example output:
```
root@kali:~# python3 shareparser.py results/
ipaddr;dns;type;share;comment;anonymous_access;user_used;authenticated_user_access
127.0.0.1;localhost;FTP;;Port 21;allowed,anonymous;;
192.168.0.10;;FTP;;Port 21,disabled,<none>;;
127.0.0.1;localhost;NFS;/mnt/test;Port 111;Read/Lookup;;;
192.168.0.10;QNAP;SMB/CIFS;Download;System default share;<none>;guest;<none>;
192.168.0.10;QNAP;SMB/CIFS;IPC$;System default share;<none>;guest;<none>;
192.168.0.10;QNAP;SMB/CIFS;Multimedia;System default share;<none>;guest;<none>;
192.168.0.10;QNAP;SMB/CIFS;Network Recycle Bin 1;System default share;<none>;guest;<none>;
192.168.0.10;QNAP;SMB/CIFS;Private;System default share;guest;<none>;
192.168.0.10;QNAP;SMB/CIFS;Public;System default share;<none>;guest;<none>;
192.168.0.10;QNAP;SMB/CIFS;Usb;System default share;<none>;guest;<none>;
192.168.0.10;QNAP;SMB/CIFS;Web;System default share;<none>;guest;<none>;
root@kali:~#  
```

# Convert subnets to a given length
This can be very handy if e.g. you are given a huge list of subnets with verious lengths and you want to convert these to equially sized smaller subnets without duplicates.
  
Syntax:
```
$ python3 subnetfixer.py <path/to/input.txt> <prefix>
```
Example:
```
root@kali:~# cat input.txt
10.10.0.0/15
10.11.0.0/16
root@kali:~# python3 subnetfixer.py input.txt 24
10.10.1.0/24
10.10.2.0/24
10.10.3.0/24
...
10.11.1.0/24
10.11.2.0/24
root@kali:~#  
```

# Setup VLAN interfaces
A tool to easily setup multiple VLAN interfaces on Linux. It will use the highest available IP-address unless you specify a IP-address in the last argument.  

Syntax:
```
$ python3 vlancon.py add|rem <network> <interface> <vlan> [<preferred ip-addr>]
```
Example:
```
root@kali:~# python3 vlancon.py add 192.168.1.0/24 eth1 101
[+] Adding interface eth1.101 (192.168.1.0/24)  
[+] Interface added.
[+] Waiting for ARP table to update.
[+] Searching for other hosts in the VLAN.
[+] Found 24 live host in network 192.168.1.0/24
[+] Checking for an available IP-address.
[+] Using IP-address: 192.168.1.254/24
[+] Adding gateway.
[+] Gateway added.
root@kali:~#  
```
  
In order for vlancon.py to work, you need to have a connection to a trunk port of a switch. I recommend getting an Ethernet to USB dongle to have a seperate interface just for this.  
  
## Use cases and Tips

The following scenarios assumes that the gateways have the first available IP-address in each VLAN. For example: 192.168.1.1/24

### Routing traffic
If you want to route traffic through a certain VLAN, as for example Internet traffic, add a default route via the target VLANs gateway:
```
root@kali:~# python3 vlancon.py add 192.168.1.0/24 eth1 101
root@kali:~# ip route add default via 192.168.1.1
```

### "Comma" VLANs
If you encounter a VLAN with the name e.g. 101,2 you need to strip the comma part and use the subnet for the "parent" VLAN. Then manually add a static route to the target VLAN via a gateway. See the following example below:
  
VLAN List:
```
101    192.168.1.0/24
101,1  192.168.2.0/24
101,2  192.168.3.0/24
```

If you want a connection to 192.168.3.0/24, then do the following:
```
root@kali:~# python3 vlancon.py add 192.168.1.0/24 eth1 101
root@kali:~# ip route add 192.168.3.0/24 via 192.168.1.1
```

### Automate connection to multiple VLANs
If you want to connect to multiple VLANs simultaneously, then you could make a script like this:
```
root@kali:~# cat connect_all.sh
python3 vlancon.py add 192.168.1.0/24 eth1 101 &
python3 vlancon.py add 192.168.2.0/24 eth1 102 &
python3 vlancon.py add 192.168.3.0/24 eth1 103 &
python3 vlancon.py add 192.168.4.0/24 eth1 104 &
wait
exit
root@kali:~# ./connect_all.sh
```
  
