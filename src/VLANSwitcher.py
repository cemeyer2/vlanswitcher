#!/usr/bin/env python

'''
Created on May 4, 2010

@author: Charlie Meyer
'''

import optparse, subprocess, re, sys

def __refresh_arp_cache(ip_addr):
    """
    refreshes the local system arp cache for a given ip address by pinging it
    """
    print "refreshing local arp cache via ping to " + str(ip_addr)
    command = ["ping","-c","1",ip_addr]
    proc = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = proc.stdout.readline().strip()
        #print line
        if line == '' and proc.poll() != None:
            break    

def ip_to_mac(ip_addr):
    """
    parses the arp cache of the local system to find a corresponding MAC address for a given IP address
    """
    __refresh_arp_cache(ip_addr)
    #http://xiix.wordpress.com/2008/06/26/python-regex-for-mac-addresses/
    mac_regex = "([a-fA-F0-9]{2}[:|\-]?){6}"
    retval = None
    command = "ip"
    arg = "neighbor"
    proc = subprocess.Popen([command, arg],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = proc.stdout.readline().strip()
        if line.find(ip_addr) >= 0: #we found an arp cache entry for the ip we were looking for
            c = re.compile(mac_regex).finditer(line)
            if c:
                for y in c:
                    retval = line[y.start(): y.end()]

        if line == '' and proc.poll() != None:
            break
    return retval

def mac_to_vm(mac_addr):
    """
    parses the virtualbox vm listings to find the name of the virtual machine with the MAC address specified
    """
    pattern = "^(Name:)(\s+)(\S+)$"
    regex = re.compile(pattern)
    retval = None
    recent_vm_name = ""
    command = ["VBoxManage", "list","-l","vms"]
    proc = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = proc.stdout.readline().strip()
        match = regex.match(line)
        if match:
            recent_vm_name = match.group(3)
        if line.find(mac_addr) >= 0:
            retval = recent_vm_name
        if line == '' and proc.poll() != None:
            break
    return retval

def switch_vm_vlan(vm_name, target_vlan):
    for nic_number in range(1,9): #can have nics numbered 1-8, so be sure to change all of them
        command = ["VBoxManage","controlvm", vm_name, "nic"+str(nic_number), "bridged", "eth0."+str(target_vlan)]
        proc = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            line = proc.stdout.readline().strip()
            if line == '' and proc.poll() != None:
                break

if __name__ == '__main__':
    #option parsing setup
    parser = optparse.OptionParser()
    parser.add_option('--ip', dest='ip_addr', metavar='IP', help='IP address of VM to switch')
    parser.add_option('--target-vlan', dest='target_vlan', metavar='VLAN', help='VLAN to switch VM to')
    (options, args) = parser.parse_args()
    
    #option parsing error checking
    if not options.ip_addr:
        parser.error("IP address of VM to switch not specified")    
    if not options.target_vlan:
        parser.error("Target VLAN not specified")
    
    #meat of the script
    mac_addr = ip_to_mac(options.ip_addr)
    if mac_addr is None:
        print "Failed to find MAC address for IP "+str(options.ip_addr)
        sys.exit(1)
    #the local arp cache gives us MAC addresses in lower case separated by colons, while the vbox
    #listing is in upper case with no separations, so conversion is necessary
    mac_addr = mac_addr.replace(":","").upper()
    print "Found MAC address for "+str(options.ip_addr)+" to be "+str(mac_addr)
    vm_name = mac_to_vm(mac_addr)
    if vm_name is None:
        print "Failed to find VM for MAC address "+str(mac_addr)
        sys.exit(1)
    print "Found VM to be "+str(vm_name)
    switch_vm_vlan(vm_name, options.target_vlan)
    print "All interfaces on VM "+str(vm_name)+" switched to VLAN "+str(options.target_vlan)
    sys.exit(0)
        
    