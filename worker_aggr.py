#!/usr/bin/python

# Usage: 
# worker_aggr.py <title> <group> <some apache access log[.gz]>
# or
# worker_aggr.py <title> <group> config

import re, sys
from datetime import datetime,timedelta

from utils import *

INTERVALS=[.5,1,2,5]
limits={'05':dict(w=500,c=1000),
        '1':dict(w=500,c=600),
        '2':dict(w=40,c=50),
        '5':dict(w=30,c=40),}

colors={
  '05':'00FF00',
  '1':'88FF00',
  '2':'FFFF00',
  '5':'FF8800',
}
limit=getlimit()

counters={'others':0}
for val in INTERVALS:
  counters[str(val)]=0

def print_config(title,group):
  print "graph_title Apache latency: %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel number of pages"
  print "graph_category %s"%group
  for val in INTERVALS:
    key=str(val).replace('.','')
    print "numbers%s.label pages served in %s secs"%(key,val)
    print "numbers%s.draw AREASTACK"%key
    print "numbers%s.colour %s"%(key,colors[key])
#    print "numbers%s.warning %s"%(key,limits[key]['w'])
#    print "numbers%s.critical %s"%(key,limits[key]['c'])

  print "numbersother.label more"
  print "numbersother.draw AREASTACK"
  print "numbersother.colour FF0000"
#  print "numbersother.warning 5"
#  print "numbersother.critical 10"


if len(sys.argv)>3:
  title=sys.argv[1]
  group=sys.argv[2]
  filename=sys.argv[3]
  if filename=='config':
    print_config(title,group)
  else:
    fi=open(filename,'r')
    for row in fi:
      if is_valid_line(row,['text/html',],[200,]):
        lat=get_lat(row)
        ctype=get_ctype(row)
        dt=get_date(row)
        bytes=get_bytes(row)

        if lat is not None and ctype in VALID_CTYPES and bytes>0 and dt>limit:
          md=ft(lat)
          pos=0
          while pos<len(INTERVALS) and INTERVALS[pos]<md :
            pos+=1

          if pos<len(INTERVALS):
            idx=str(INTERVALS[pos])
            counters[idx]+=1
          else:
            counters['others']+=1

    tot=sum(counters.values())

    for threshould in INTERVALS:
      val=counters[str(threshould)]
      print "numbers%s.value %s"%(str(threshould).replace('.',''),val)

    val=counters['others']
    print "numbersother.value %s"%val










