#!/usr/bin/python

# Usage:
# worker_ldap.py <title> <group> 
# or
# worker_ldap.py <title> <group> config


import ldap
import time
import sys

#(ip, login, pwd)
SERVERS=[('x.x.x.x','cn=xxx','xxx'),]


def print_config(title,group):
  print "graph_title LDAP latency: %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel seconds"
  print "graph_category %s"%group
  for ip,login,pwd in SERVERS:
    id=ip.replace('.','_')
    print "server%s.label %s"%(id,ip)

if len(sys.argv)>2:
  title=sys.argv[1]
  group=sys.argv[2]
  if len(sys.argv)>3:
    print_config(title,group)
  else:
    for ip,login,pwd in SERVERS:
      id=ip.replace('.','_')
      start=time.time()
      try:
        l=ldap.open(ip)
        l.simple_bind(login, pwd)
      except ldap.LDAPError, e:
        pass
      stop=time.time()

      print "server%s.value %s"%(id,stop-start)
