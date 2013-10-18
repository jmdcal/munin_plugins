#!/usr/bin/python2.7

import sys
from collections import Counter
from utils import *
from etc.env import INTERVALS
from etc.env import COLORS

limit=getlimit()


def print_config(title,group):
  print "graph_title Nginx latency (new): %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel number of pages"
  print "graph_category %s"%group
  for val in INTERVALS:
    key=str(val).replace('.','')
    print "numbers%s.label pages served in %s secs"%(key,val)
    print "numbers%s.draw AREASTACK"%key
    print "numbers%s.colour %s"%(key,COLORS[key])

  print "numbersother.label more"
  print "numbersother.draw AREASTACK"
  print "numbersother.colour FF0000"


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
      counters=Counter(others=0)
      for val in INTERVALS:
        counters[str(val)]=0
      
      fi=open(filename,'r')
      for row in fi:
        datas=RowParser(row)
        if datas.is_valid_line([200,]):
          lat=datas.get_latency()
          dt=datas.get_date()
          bytes=datas.get_bytes()

          if lat is not None and bytes>0 and dt>limit:
            md=ft(lat)
            pos=0
            while pos<len(INTERVALS) and INTERVALS[pos]<md :
              pos+=1

            if pos<len(INTERVALS):
              idx=str(INTERVALS[pos])
              counters[idx]=1+counters[idx]
            else:
              counters['others']=1+counters['others']

      tot=sum(counters.values())

      for threshould in INTERVALS:
        val=counters[str(threshould)]
        print "numbers%s.value %s"%(str(threshould).replace('.',''),val)

      val=counters['others']
      print "numbersother.value %s"%val
    
    
   
  
  
  









