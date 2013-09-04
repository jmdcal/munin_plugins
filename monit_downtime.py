#!/usr/bin/python2.7

# Usage monit_downtime.py [config]

import re  
import sys
import fcntl
import time
import subprocess

from utils import *
from etc.env import MONIT_STATUS
from etc.env import MONIT_PARSER
from etc.env import MONIT_PERCENTAGE_GRAPH
from etc.env import MONIT_FULL
from etc.env import CACHE_MONIT

def print_config(title,group,vals):
  print "graph_title %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel status"
  print "graph_category %s"%group
  print "failedtest.label monit down"
  print "failedtest.draw AREASTACK"
  print "failedtest.colour 757575"
  
  vals.remove('failedtest')
  for l in vals:
    #get color if available
    c=MONIT_STATUS.get(l,None)
    id=l.replace(' ','_')
    print "%s.label %s" % (id,l)
    print "%s.draw AREASTACK" % id
    if c is not None:
      print "%s.colour %s"  % (id,c)
    
def parse_monit_row(row):
  status=None
  try:
    groups=MONIT_PARSER.match(row).groups()
  except AttributeError:
    pass
  else:
    status=groups[2].lower().strip()
  return status

#We init at least with failedtest counter
to_init=['failedtest',]
if MONIT_FULL:
  to_init+=MONIT_STATUS.keys()

counts=CacheCounter(CACHE_MONIT,to_init)

if len(sys.argv)>1 and sys.argv[1]=='config':
  print_config('Monit status','monit',counts.keys())
else:  
  csensors=1
  try:
    pid=int(subprocess.check_output(['pidof','monit']).strip())
  except (subprocess.CalledProcessError, ValueError):
    #if fails means that the process is not running
    counts['failedtest']=1
  else:
    csensors=0
    sensors=subprocess.check_output(['monit','summary'])
    for row in sensors.split('\n'):
      status=parse_monit_row(row)
      if status is not None:
        counts[status]=counts[status]+1
        csensors+=1

  norm=lambda x:x
  if MONIT_PERCENTAGE_GRAPH:
    norm=lambda x:(x*100/csensors)
    
  for l,v in counts.most_common():
    id=l.replace(' ','_')
    print "%s.value %s"% (id,norm(v))
      
counts.store_in_cache()
  
