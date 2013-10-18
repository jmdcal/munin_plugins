#!/usr/bin/python2.7

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


is_config=(len(sys.argv)>1 and sys.argv[1]=='config')
files=getparams_from_config()

if len(files)<1:
  sys.stderr.write('Not configured: see documentation')
else:
  for title,group,filename in files:
    print "multigraph nginx_%s_%s"%('aggr',filename.replace('/','_').replace('.','_'))
    
    if is_config:
      print_config(title,group)
    else:
      fi=open(filename,'r')
      counters=Counter()
      items=HTTP_CODES.keys()
      for k in items:
        counters[k]=0
      for row in fi:
        datas=RowParser(row)
        if datas.is_valid_line(HTTP_CODES.keys()):
          lat=datas.get_latency()
          dt=datas.get_date()
          try:
            code=int(datas.get_code())
          except ValueError: 
            pass #Something get wrong with parser
          else:
            if lat and dt>limit:
              counters[code]=1+counters[code]
      for k in sorted(items):
        print "code%s.value %s"%(k,counters[k])
