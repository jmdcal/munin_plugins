#!/usr/bin/python2.7

# Usage: 
# worker_http.py <title> <group> <some apache access log[.gz]>
# or
# worker_http.py <title> <group> <some apache access log[.gz]> config

import sys
import re
import commands
import tempfile
import os
from datetime import datetime,timedelta
import time

from collections import Counter

from utils import *

from etc.env import HTTP_CODES

def print_config(title,group):
  print "graph_title Nginx http codes: %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel q.ty"
  print "graph_category %s"%group
  hci=HTTP_CODES.items()
  hci.sort()
  for k,v in hci:
    print "code%s.label [%s] %s (last %s minutes)"%(k,k,v,MINUTES)
#    print "code%s.type GAUGE"%k
#    print "code%s.min 0"%k
#    print "code%s.warning %s"%(k,limits[k/100]['w'])
#    print "code%s.critical %s"%(k,limits[k/100]['c'])

limit=getlimit()

if len(sys.argv)>3:
  title=sys.argv[1]
  group=sys.argv[2]
  filename=sys.argv[3]
  if len(sys.argv)>4:
    if sys.argv[4]=='config':
      print_config(title,group)
  else:
    fi=open(filename,'r')
    counters=Counter()
    items=HTTP_CODES.keys()
    for k in items:
      counters[k]=0
    for row in fi:
      datas=RowParser(row)
      if datas.is_valid_line(row,[]):
        lat=datas.get_latency()
        dt=datas.get_date()
        code=datas.get_code()
        if lat and dt>limit and code in HTTP_CODES:
            counters[code]=1+counters[code]
    for k in sorted(items):
      print "code%s.value %s"%(k,counters[k])
