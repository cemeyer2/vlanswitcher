#!/usr/bin/env python

'''
Created on May 4, 2010

@author: Charlie Meyer
'''

import optparse, subprocess, re

def refresh_arp_cache(ip_addr):
    print "refreshing local arp cache via ping to " + str(ip_addr)
    command = ["ping","-c","1",ip_addr]
    proc = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = proc.stdout.readline().strip()
        #print line
        if line == '' and proc.poll() != None:
            break    

def ip_to_mac(ip_addr):
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
    retval = None
    command = ["VBoxManage", "list","-l","vms"]
    proc = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = proc.stdout.readline().strip()
        print line
        if line == '' and proc.poll() != None:
            break

def switch_vm_vlan(vm_name, target_vlan):
    pass

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('--ip', dest='ip_addr', metavar='IP', help='IP address of VM to switch')
    parser.add_option('--target-vlan', dest='target_vlan', metavar='VLAN', help='VLAN to switch VM to')
    (options, args) = parser.parse_args()
    
    if not options.ip_addr:
        parser.error("IP address of VM to switch not specified")
        
    if not options.target_vlan:
        parser.error("Target VLAN not specified")
    
    refresh_arp_cache(options.ip_addr)
    mac_addr = ip_to_mac(options.ip_addr)
    mac_addr = mac_addr.replace(":","").upper()
    print "Found MAC address for "+str(options.ip_addr)+" to be "+str(mac_addr)
    vm_name = mac_to_vm(mac_addr)
        
    