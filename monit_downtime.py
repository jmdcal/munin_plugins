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
  print "failedtest.warning 6"
  print "failedtest.critical 12"

def lock_fn(fd):
  #locking file
  locked=False
  while not locked:
    try:
      fcntl.lockf(fd,fcntl.LOCK_EX)
    except IOError:
      time.sleep(3)
    else:
      locked=True

def unlock_fn(fd):
  fcntl.lockf(fd, fcntl.LOCK_UN)
  
def open_and_update(fn):
  count=0
  #open file to check how many time
  try:
    #it exists
    fd=open(fn,'r+')
  except IOError:
    #it not exists
    fd=open(fn,'w')
  
  lock_fn(fd)

  #try to get previous value
  try:
    count=int(fd.read())
  except:
    count=0
    
  count+=1
  fd.seek(0)    
  fd.write(str(count))
  fd.truncate()
  unlock_fn(fd)
  fd.close()  

  return count


if len(sys.argv)>1 and sys.argv[1]=='config':
  print_config('Monit downtime','monit')
else:
  count=0
  try:
    pid=int(subprocess.check_output(['pidof','monit']).strip())
  except (subprocess.CalledProcessError, ValueError):
    #if fails means that the process is not running
    count=open_and_update(DOWNTIME_COUNTER)               
    
  print "failedtest.value %s"%count
  

