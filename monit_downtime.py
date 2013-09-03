#!/usr/bin/python2.7

# Usage monit_downtime.py [config]

import re  
import sys
import fcntl
import time
import subprocess

from collections import Counter

from etc.env import MONIT_STATUS
from etc.env import MONIT_PARSER

def print_config(title,group):
  print "graph_title %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel status"
  print "graph_category %s"%group
  print "failedtest.label monit down"
  print "failedtest.draw AREASTACK"
  print "failedtest.colour 757575"
  for l,c in MONIT_STATUS.items():
    id=l.replace(' ','_')
    print "%s.label %s" % (id,l)
    print "%s.draw AREASTACK" % id
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

  
if len(sys.argv)>1 and sys.argv[1]=='config':
  print_config('Monit status','monit')
else:
  counts=Counter()
  counts['failedtest']=0
  for l in MONIT_STATUS.keys():
    counts[l]=0
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

  for l,v in counts.most_common():
    id=l.replace(' ','_')
    print "%s.value %s"% (id,v*100/csensors)
    
  print "failedtest.value %s"% (counts['failedtest']*100/csensors)

  
  
