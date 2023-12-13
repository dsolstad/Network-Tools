#!/usr/bin/env python3
##
## A tool to easily add and remove vlans.
## Author: Daniel Solstad (dsolstad.com)
## Version: 1.2
##

import sys

if not sys.version_info[0] == 3:
    print ("You need to run this with python3")
    sys.exit()

import os
import time
import re
import subprocess as sub
import ipaddress
from termcolor import colored

if not os.geteuid() == 0:
    print ("You need to run this with sudo")
    sys.exit()

help = """
vlancon.py add|rem <network/<cidr>> <interface> <vlan nr> [<preferred IP-addr>]

Example:
vlancon.py add 192.168.1.0/24 eth1 101
vlancon.py add 192.168.1.0/24 eth1 101 192.168.1.50
vlancon.py rem 192.168.1.0/24 eth1 101
"""

def check_interface(interface):
    p = sub.Popen(['ip', 'link', 'show', interface], stdout=sub.PIPE, stderr=sub.PIPE)
    res, err = p.communicate()
    if err.decode('ascii').find('does not exist') == -1:
        return True
    return False
        
def vlan_add(interface, vlan):
    subinterface = interface + "." + vlan
    sub.call(['vconfig', 'add', interface, vlan], stdout=sub.PIPE, stderr=sub.PIPE)
    sub.call(['ip', 'link', 'set', 'dev', interface, 'up'], stdout=sub.PIPE, stderr=sub.PIPE)
    sub.call(['ip', 'link', 'set', 'dev', subinterface, 'up'], stdout=sub.PIPE, stderr=sub.PIPE)

def vlan_rem(interface, vlan):
    subinterface = interface + "." + vlan
    #sub.call(['ip', 'link', 'set', 'dev', interface, 'down'], stdout=sub.PIPE, stderr=sub.PIPE)
    sub.call(['ip', 'link', 'set', 'dev', subinterface, 'down'], stdout=sub.PIPE, stderr=sub.PIPE)
    sub.call(['vconfig', 'rem', subinterface], stdout=sub.PIPE, stderr=sub.PIPE)

def route_add(network, interface, vlan):
    subinterface = interface + "." + vlan    
    #sub.call(['ip', 'route', 'add', 'default', 'via', gateway, 'dev', subinterface], stdout=sub.PIPE, stderr=sub.PIPE)
    sub.call(['ip', 'route', 'add', network, 'dev', subinterface], stdout=sub.PIPE, stderr=sub.PIPE)

def route_rem(network, interface, vlan):
    subinterface = interface + "." + vlan    
    #sub.call(['ip', 'route', 'del', 'default', 'via', gateway, 'dev', subinterface], stdout=sub.PIPE, stderr=sub.PIPE)
    sub.call(['ip', 'route', 'del', network, 'dev', subinterface], stdout=sub.PIPE, stderr=sub.PIPE)

def ipaddr_set(interface, vlan, ipaddr):
    subinterface = interface + "." + vlan
    sub.call(['ip', 'addr', 'add', ipaddr, 'dev', subinterface], stdout=sub.PIPE, stderr=sub.PIPE)

def find_live_hosts(interface, vlan, network):
    cmd = ['arp-scan', '--interface=' + interface + '.' + vlan , network, '--arpspa', '0.0.0.0']
    p = sub.Popen(cmd, stdout=sub.PIPE, stderr=sub.PIPE)
    res, err = p.communicate()
    # Filter out all valid IP addresses
    ips = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', res.decode('ascii'))
    return ips

# To determine an available ipaddr, we need to arp-scan the network to find live hosts.
# However, this can give unacurrate results if the network is not ready.
# It is usually ready after 100 seconds, or when the ARP table gets populated.
def wait_for_arp(interface, vlan, network):
    subinterface = interface + '.' + vlan
    for i in range(1, 50):
        try:
            res = sub.check_output(['arp', '-a', '-i', subinterface]).decode('ascii')
            # If there no incomplete entries we return
            if res.find('incomplete') == -1 and res.find('no match') == -1:
                return True
        except: pass
        time.sleep(2)
    return False

# Checking if the gateway is responsive. Waiting 60 seconds.
def check_gateway(gateway):
    for i in range(1, 60):
        try:
            res = sub.check_output(['ping', '-c', '1', gateway]).decode('ascii')
            if res.find('1 received') != -1:
                return True
        except: pass
        time.sleep(1)
    return False

# Gets the last octet of all valid IP addresses in the network range
def get_ip_range(network):
    net = ipaddress.ip_network(network)
    ip_range = []
    for addr in list(map(str, net.hosts())):
        ip_range.append(addr)
    return ip_range


if __name__ == "__main__":

    if len(sys.argv) == 1:
        print (help)
        sys.exit(1)

    network = sys.argv[2]       # e.g 192.168.1.0/24
    interface = sys.argv[3]     # e.g eth1
    vlan = sys.argv[4]          # e.g 101
    #gateway = sys.argv[5]      # e.g 192.168.1.1

    if sys.argv[1] == 'rem':
        if len(sys.argv) != 5:
            print (colored('Expecting 4 arguments', 'red'))
            print (help)
            sys.exit(1)

        print ('[+] Removing vlan interface: ' + interface + '.' + vlan)
        vlan_rem(interface, vlan)
        print ('[+] Removing route.')
        route_rem(network, interface, vlan)
        print (colored('Done.', 'green'))

    elif sys.argv[1] == 'add':
        if len(sys.argv) < 5:
            print (colored('Missing one or more arguments', 'red'))
            print (help)
            sys.exit(1)

        if not check_interface(interface):
            print (colored('[+] Interface ' + interface + ' does not exist', 'red'))
            sys.exit()

        print ('[+] Adding interface ' + interface + '.' + vlan + ' (' + network + ')')
        vlan_rem(interface, vlan)
        vlan_add(interface, vlan)
        print (colored('[+] Interface added.', 'green'))
        
        print ('[+] Waiting for network to be ready.')
        wait_for_arp(interface, vlan, network)

        print ('[+] Searching for other hosts in the VLAN.')
        ips = find_live_hosts(interface, vlan, network)
        if (len(ips)) > 0:
            print (colored('[+] Found the following ' + str(len(ips)) + ' live host in network ' + network, 'green'))
            print ("\n".join(ips))
        else:
            print (colored('[+] Found 0 live host. Tip: Verify cabling.', 'red'))

        cidr = network.split('/')
        ipaddr = False

        # Preferred IP-address argument given.
        if len(sys.argv) == 6:
            print ('[+] Checking if the preferred IP-address is available.')
            pref_ip = sys.argv[5]
            if pref_ip not in ips:
                ipaddr = pref_ip + '/' + cidr[1]
            else:
                print (colored('[+] Error - The preferred IP-address is not available. Aborting.', 'red'))
                sys.exit(1)
        # Letting the script figure out an available IP-address
        else:
            print ('[+] Checking for an available IP-address.')
            for addr in reversed(get_ip_range(network)):
                if addr not in ips:
                    ipaddr = addr + '/' + cidr[1]
                    break

        if ipaddr != False:
            ipaddr_set(interface, vlan, ipaddr)
            print (colored('[+] Using IP-address: ' + str(ipaddr), 'green'))
        else:
            print (colored('[+] Error - Could not find any available IP addresses. Aborting.', 'red'))
            sys.exit(1)
        
        print ("[+] Adding route.")
        route_add(network, interface, vlan)
        print (colored('[+] Route added.', 'green'))

        #print ("[+] Checking if gateway is responding")
        #if check_gateway(gateway):
        #print (colored('[+] Success. Gateway responding.', 'green'))
        #else:
        #    print (colored('[+] Error - No respons from gateway.', 'red'))
        #    sys.exit(1)

    else:
        print (colored('Missing one or more arguments', 'red'))
        print (help)
        sys.exit(1)
