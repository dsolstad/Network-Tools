# NMAP-Tools

A collection of scripts built around Nmap.  
  
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

## nmapuniqueports.py - Get unique ports from Nmap scans
$ nmapuniqueports.py &lt;path/to/folder&gt;
```
root@kali:~# python3 nmapuniqueports.py Results/
21,22,23,25,53,80,81,88,89,111,135,139,161,389,427,443,445
root@kali:~# 
```

