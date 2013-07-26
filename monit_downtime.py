#!/usr/bin/python2.7

# Usage monit_downtime.py [config]

import re  
import sys
import fcntl
import time
import subprocess

from etc.env import DOWNTIME_COUNTER  


monit_status={
  "online with all services":'00FF00',
  "running":'00FF00',
  "accessible":'00FF00',  
  "monitored":'FFFF00',
  "initializing":'FFFF00',
  "action done":'FFFF00', 
  "checksum succeeded":'FFFF00',
  "connection succeeded":'FFFF00',
  "content succeeded":'FFFF00',
  "data access succeeded":'FFFF00',
  "execution succeeded":'FFFF00',
  "filesystem flags succeeded":'FFFF00',
  "gid succeeded":'FFFF00',
  "icmp succeeded":'FFFF00',
  "monit instance changed not":'FFFF00',
  "type succeeded":'FFFF00',
  "exists":'FFFF00',
  "permission succeeded":'FFFF00',
  "pid succeeded":'FFFF00',
  "ppid succeeded":'FFFF00',
  "resource limit succeeded":'FFFF00',
  "size succeeded":'FFFF00',
  "timeout recovery":'FFFF00',
  "timestamp succeeded":'FFFF00',
  "uid succeeded":'FFFF00',
  "not monitored":'FF0000',
  "checksum failed":'FF0000',
  "connection failed":'FF0000',
  "content failed":'FF0000',
  "data access error":'FF0000',
  "execution failed":'FF0000',
  "filesystem flags failed":'FF0000',
  "gid failed":'FF0000',
  "icmp failed":'FF0000',
  "monit instance changed":'FF0000',
  "invalid type":'FF0000',
  "does not exist":'FF0000',
  "permission failed":'FF0000',
  "pid failed":'FF0000',
  "ppid failed":'FF0000',
  "resource limit matched":'FF0000',
  "size failed":'FF0000',
  "timeout":'FF0000',
  "timestamp failed":'FF0000',
  "uid failed":'FF0000',
}

def print_config(title,group):
  print "graph_title %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel n. of test failed"
  print "graph_category %s"%group
  print "failedtest.label monit down"
  print "failedtest.draw AREASTACK"
  print "failedtest.colour FF0000"
  print "failedtest.warning 6"
  print "failedtest.critical 12"
  for l,c in monit_status.items():
    id=l.replace(' ','_')
    print "%s.label %s" % (id,l)
    print "%s.draw AREASTACK" % id
    print "%s.colour %s"  % (id,c)

def parse_monit_row(row):
  status=None
  monit_re=(
    r'^(Filesystem|Directory|File|Process|Remote Host|System|Fifo)'
    r"\s('.*?')"
    r'\s(.*)'
  )

  try:
    groups=re.match(monit_re,row).groups()
  except AttributeError:
    pass
  else:
    status=groups[2].lower().strip()

  return status

  
if len(sys.argv)>1 and sys.argv[1]=='config':
  print_config('Monit downtime','monit')
else:
  counts={}
  counts['failedtest']=0
  for l in monit_status.keys():
    counts[l]=0

  csensors=0
  try:
    pid=int(subprocess.check_output(['pidof','monit']).strip())
  except (subprocess.CalledProcessError, ValueError):
    #if fails means that the process is not running
    counts['failedtest']=1
    csensors=1
  else:
    sensors=subprocess.check_output(['monit','summary'])
    for row in sensors.split('\n'):
      status=parse_monit_row(row)
      if status is not None:
        counts[status]=counts[status]+1
        csensors+=1

  for l in monit_status.keys():
    id=l.replace(' ','_')
    print "%s.value %s [%s %s]"% (id,counts[l]*100/csensors)
  print "failedtest.value %s"% (counts['failedtest']*100/csensors)

  
  