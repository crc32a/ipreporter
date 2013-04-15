#!/usr/bin/env python

import xmlrpclib
import json
import sys
import os
import re

CONF_FILE = "~/ipreporter.json"

link_re = re.compile("^(.*[^\s])\s+Link encap:.*$")
ipv4_re = re.compile("\s+inet addr:\s*([^\s]+)\s+.*")
ipv6_re = re.compile("\s+inet6 addr:\s*([^\s]+)")

def chop(line_in):
    return line_in.replace("\r","").replace("\n","")

def scan():
    out = {}
    iface = ""
    for line in os.popen("ifconfig","r").readlines():
        chopped = chop(line)
        m = link_re.match(chopped)
        if m:
            iface = m.group(1)
            out[iface] = {"ipv4":"","ipv6":""}
        m = ipv4_re.match(chopped)
        if m:
            out[iface]["ipv4"]=m.group(1).strip()
        m = ipv6_re.match(chopped)
        if m:
            out[iface]["ipv6"]=m.group(1).strip().split("/")[0]
    return out


def printf(format,*args): sys.stdout.write(format%args)

def load_json(json_file):
    full_path = os.path.expanduser(json_file)
    full_path = os.path.abspath(full_path)
    fp = open(full_path,"r")
    json_data = fp.read()
    fp.close()
    out = json.loads(json_data)
    return out


def save_json(json_file,obj):
    full_path = os.path.expanduser(json_file)
    full_path = os.path.abspath(full_path)
    fp = open(full_path,"w")
    out = json.dumps(obj, indent=2)
    fp.write(out)
    fp.close()


def expandpath(file_path):
    return os.path.abspath(os.path.expanduser(file_path))



class IpReporterClient(object):
    def __init__(self,conf_file=CONF_FILE):
        conf = load_json(conf_file)
        url = conf["url"]
        cred = conf["cred"]
        self.conf = conf
        self.s = xmlrpclib.ServerProxy(url,allow_none=True)
        self.cred = cred

    def setIp(self,name,val):
        return self.s.setIp(self.cred,name,val)

    def getIp(self,name):
        return self.s.getIp(self.cred,name)

    def delIp(self,name):
        return self.s.delIp(self.cred,name)

    def getAll(self):
        return self.s.getAll(self.cred)

    def delAll(self):
        return self.s.delAll(self.cred)

    def setMyIps(self):
        self.s.delAll(self.cred)        
        ips = scan()
        for (iface,ip_addrs) in ips.iteritems():
            for (ip_type,ip_addr) in ip_addrs.iteritems():
                name = "%s_%s"%(iface,ip_type)
                self.setIp(name,ip_addr)


    def echo(self,param):
        printf("%s\n",self.s.echo(self.cred,param))
	
