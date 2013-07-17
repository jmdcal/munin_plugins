#!/usr/bin/python2.7

# Usage monit_downtime.py [config]

import re
import sys
import fcntl
import time
import subprocess

from etc.env import DOWNTIME_COUNTER

def print_config(title,group):
  print "graph_title %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel n. of test failed"
  print "graph_category %s"%group
  print "failedtest.label test failed"
  print "failedtest.draw AREASTACK"
  print "failedtest.colour FF0000"


if len(sys.argv)>1 and sys.argv[1]=='config':
  print_config('Monit downtime','monit')
else:
  try:
    pid=int(subprocess.check_output(['pidof','monit']).strip())
  except subprocess.CalledProcessError, ValueError:
    #open file to check how many time
    try:
      #it exists
      fd=open(DOWNTIME_COUNTER,'r+')
    except IOError:
      #it not exists
      fd=open(DOWNTIME_COUNTER,'w')
      
    #locking file
    locked=False
    while not locked:
      try:
        fcntl.lockf(fd,fcntl.LOCK_EX)
      except IOError:
        time.sleep(3)
      else:
        locked=True
    count
        
    #try to get previous value
    try:
      count=int(fd.read())
    except IOError,ValueError:
      #IOError means that file is open in W mode
      #ValueError means that file doesn't contains an int
      count=0
      
    count+=1
    
    fd.seek(0)    
    fd.write(count)
    fd.truncate()
    fd.close()
  else
    #ok we will return 0
    count=0
    
  print "failedtest.value %s"%count
  

