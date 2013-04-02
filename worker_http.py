#!/usr/bin/python

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

from utils import *

http_codes={
400:"Bad Request",
401:"Unauthorized",
403:"Forbidden",
500:"Internal Server Error",
502:"Bad Gateway",
503:"Service Unavailable",
504:"Gateway Timeout",
}

limits={
  4:dict(w=5,c=8),
  5:dict(w=1,c=3),
}

def print_config(title,group):
  print "graph_title Apache http codes: %s"%title
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
    counters={}
    items=http_codes.items()
    for k,v in items:
      counters[k]=0
    for row in fi:
      if is_valid_line(row,['text/html',],[]):
        lat=get_lat(row)
        ctype=get_ctype(row)
        dt=get_date(row)
        bytes=get_bytes(row)
        code=get_code(row)
        if lat and dt>limit and code in http_codes:
            counters[code]+=1
    items.sort()
    for k,v in items:
      print "code%s.value %s"%(k,counters[k])
