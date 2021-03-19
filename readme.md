### Table of Contents

[Merge multiple nmap scans into one CSV](https://github.com/dsolstad/Network-Tools#Merge multiple nmap scans into one CSV)

[Get unique open ports from Nmap scans](https://github.com/dsolstad/Network-Tools#Get unique open ports from Nmap scans)

[Resolve all hostnames from a list](https://github.com/dsolstad/Network-Tools#Resolve all hostnames from a list)

[Network segmentation testing](https://github.com/dsolstad/Network-Tools#Network segmentation testing)

[Setup VLAN interfaces](https://github.com/dsolstad/Network-Tools#Setup VLAN interfaces)

# Merge multiple nmap scans into one CSV
The script recursively goes through the given folder to find all .nmap files and presents a combined CSV of the results.  
$ nmapmerge.py &lt;path/to/folder&gt;
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

# Get unique open ports from Nmap scans
Recursively goes through the given folder (e.g. ./results), parses all the files and presents a list of unique ports open. Works for .nmap files.
```
root@kali:~# grep -Er '^[0-9]{1,6}\/[tcp|udp]' results/ | grep open | cut -d':' -f2 | cut -d'/' -f1 | sort -n -u | tr '\n' ','
21,22,23,25,53,80,81,88,89,111,135,139,161,389,427,443,445
root@kali:~# 
```
  
# Get unique IP-addresses from Nmap scans
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
  
$ python3 nmapsegtest.py &lt;network&gt;
  
Pro tip: You can use xargs to do multiple Nmap scans in parallel. Just be sure to find the right number for your network, before you start to lose accuracy. The targets.txt can contain any number of subnets/hosts (separated by newlines). The following command will only run three Nmap processes simultaneously at any given time until the all the targets are scanned.
  
```
$ cat targets.txt | xargs -I CMD -P 3 python3 nmapsegtest.py CMD
```

# Setup VLAN interfaces
A tool to easily setup multiple VLAN interfaces on Linux. It will use the highest available IP-address unless you specify a IP-address in the last argument.  

Syntax:    
$ python3 vlancon.py add|rem &lt;network&gt; &lt;interface&gt; &lt;vlan&gt; [&lt;preferred ip-addr&gt;]

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

### Comma VLANs
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
  
