# NMAP-Tools

A collection of scripts built around Nmap.  

## nmapmerge.py - Merge multiple Nmap ouputs into one CSV
$ nmapmerge.py &lt;path/to/folder&gt;
```
root@kali:~# python3 nmapmerge.py Results/
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
python3 nmapmerge.py Results/ | grep open | grep -v filtered
```

## Get unique open ports from Nmap scans
```
root@kali:~# grep -Er '^[0-9]{1,6}\/[tcp|udp]' Results/ | grep open | cut -d':' -f2 | cut -d'/' -f1 | sort -n | uniq | tr '\n' ','
21,22,23,25,53,80,81,88,89,111,135,139,161,389,427,443,445
root@kali:~# 
```
  
## Get unique IP-addresses from Nmap scans
```
root@kali:~# grep -Eorh "([0-9]{1,3}\.){3}[0-9]{1,3}\." Results/ | sort | uniq
192.168.0.1
192.168.0.2
192.168.0.3
root@kali:~# 
```

## nmapsegtest.py - Optimized Nmap scan for segmentation testing

When doing a blind network scan, where every host is reported to be alive and all ports filtered, a large network scan will take forever to complete. After benchmarking Nmap and comparing results with different settings, including max-rtt-timeout,host-timeout,max-retries and min/max-hostgroup it was the rtt-timeout parameter that did the most decrease in scan time. A value of 150ms resulted in the fastest and most thorough scan for the network I assessed. Any lower value would fail to find all active services. 
  
$ python3 nmapsegtest.py &lt;network&gt;
  
Pro tip: You can use xargs to do multiple Nmap scans in parallel. Just be sure to find the right number for your network, before you start to lose accuracy. The targets.txt can contain any number of subnets (separated by newlines). The following command will only run three Nmap processes simultaneously at any given time until the all the targets are scanned.
  
```
$ cat targets.txt | xargs -I CMD -P 3 python3 nmapsegtest.py CMD
```


## nmapscan.py - Nmap scanning simplified  
This is just a wrapper around Nmap which will run a full host discovery, tcp, udp, os and version scan. It will also create output files for each host in all formats.
  
$ nmapscan.py &lt;network&gt; &lt;interface&gt; [&lt;path/to/ports.txt&gt;]
```
root@kali:~# python3 nmapscan.py 192.168.1.0/24 eth1.101
[+] No input file with ports given. Using defaults.
[+] Initiating host discovery  
[+] Found the following hosts:  
192.168.1.1  
192.168.1.2  
192.168.1.137  
192.168.1.254  
[+] Writing result to Results/192.168.1.0[24]/host_discovery.txt  
----------------------------------------  
[+] Initiating port scan on 192.168.1.1  
[+] Writing result to Results/192.168.1.0[24]/192.168.1.1/  
[+] Connect scan progress  
[XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX]  
[+] Connect scan completed  
[+] Service scan progress  
[XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX]  
[+] Scanning of 192.168.253.1 completed  
[+] Initiating port scan on 192.168.1.2
...  
root@kali:~#
```

The output folder structure example:
```
Results/192.168.0.0[24]  
       /192.168.1.0[24]/host_discovery.txt  
                        192.168.1.1/  
                        192.168.1.2/  
                        192.168.1.137/  
                        192.168.1.254/192.168.1.254.nmap  
                                      192.168.1.254.xml  
                                      192.168.1.254.gnmap  
  
```
