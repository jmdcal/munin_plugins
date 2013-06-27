#!/usr/bin/python2.7

# Usage: 
# worker_http.py <title> <group> <some apache access log[.gz]>
# or
# worker_http.py <title> <group> config

import sys
import re
import commands
import tempfile
import os
from datetime import datetime,timedelta
import time

from collections import Counter

from utils import *

from etc.env import http_codes

#limits={
#  4:dict(w=5,c=8),
#  5:dict(w=1,c=3),
#}

def print_config(title,group):
  print "graph_title Nginx http codes: %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel q.ty"
  print "graph_category %s"%group
  hci=http_codes.items()
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
  if filename=='config':
    print_config(title,group)
  else:
    fi=open(filename,'r')
    counters=Counter()
    items=http_codes.keys()
    for k in items:
      counters[k]=0
    for row in fi:
      datas=RowParser(row)
      if datas.is_valid_line(row,[]):
        lat=datas.get_latency()
        dt=datas.get_date()
        code=dats.get_code()
        if lat and dt>limit and code in http_codes:
            counters[code]=1+counters[code]
    for k in sorted(items):
      print "code%s.value %s"%(k,counters[k])
