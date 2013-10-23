#!/usr/bin/python2.7

import sys
from collections import Counter
from utils import *

from etc.env import CACHE_BOTS
from etc.env import INTERVALS
from etc.env import HTTP_CODES
from etc.env import COLORS
from etc.env import MINUTES

def print_config_aggr(title,group):
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

def print_config_bots(title,group,agents):
  print "graph_title Nginx Bots: %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel number of call"
  print "graph_category %s"%group

  for l,v in agents:
    print "%s.label %s" %(l,l)
    print "%s.warning 10" %l
    print "%s.critical 30" %l

def print_config_http(title,group):
  print "graph_title Nginx http codes: %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel q.ty"
  print "graph_category %s"%group
  hci=HTTP_CODES.items()
  hci.sort()
  for k,v in hci:
    print "code%s.label [%s] %s (last %s minutes)"%(k,k,v,MINUTES)


LABELS={
  'aggr':'number of pages',
  'bots':'number of call',
  'http':'number of response',
}


is_config=(len(sys.argv)>1 and sys.argv[1]=='config')
files=getparams_from_config()
limit=getlimit()

def print_data(id,v):
  print "%s.value %s"%(id,v)

def print_config(id,v):
  print "%s.label %s"%(id,id)

printer=print_data
if is_config:
  printer=print_config


if len(files)<1:
  sys.stderr.write('Not configured: see documentation')
else:     
  for title,group,filename in files:
    #Aggr init
    aggr_counters=Counter(others=0)
    for val in INTERVALS:
      aggr_counters[str(val)]=0

    #Bots init
    agents_counter=CacheCounter(CACHE_BOTS)
    
    #Http init
    http_counters=Counter()
    for k in HTTP_CODES.keys():
      http_counters[k]=0
           
    #read from files valid rows
    fi=open(filename,'r')
    for row in fi:
      datas=RowParser(row)
           
      if datas.get_date()>limit:        
        lat=datas.get_latency()
        bytes=datas.get_bytes()        
        code=datas.code()
        try: 
          int_code=int(code)
        except:
          int_code=-1
              
        #aggr evaluate
        if lat is not None and bytes>0 and int_code in [200,]:
          md=ft(lat)
          pos=0
          while pos<len(INTERVALS) and INTERVALS[pos]<md:
            pos+=1

          if pos<len(INTERVALS):
            idx=str(INTERVALS[pos])
            aggr_counters[idx]=1+aggr_counters[idx]
          else:
            aggr_counters['others']=1+aggr_counters['others']

        #bots evaluate
        if int_code in [200,]:
          agent=datas.get_agent()
          agent=get_short_agent(agent)
          agents_counter[agent]=1+agents_counter[agent]
          
        #http evaluate
        if int_code in HTTP_CODES.keys():
          http_counters[code]=http_counters[code]+1
    
    #Aggr prints
    print "multigraph nginx_%s_%s"%('aggr',filename.replace('/','_').replace('.','_'))
    if is_config:
      print_config_aggr(title,group)
    
    for threshould in INTERVALS:
      id="numbers%s"%str(threshould).replace('.','')
      v=aggr_counters[str(threshould)]            
      printer(id,v)

    id="numbersother"
    v=aggr_counters['others']            
    printer(id,v)
    
    #Bots prints
    print "multigraph nginx_%s_%s"%('bots',filename.replace('/','_').replace('.','_'))
    if is_config:
      print_config_bots(title,group,agents_counter)
    
    for l,v in agents_counter:
      printer(l,v)
          
    #Http prints
    print "multigraph nginx_%s_%s"%('http',filename.replace('/','_').replace('.','_'))
    if is_config:
      print_config_http(title,group)

    for k in sorted(HTTP_CODES.keys()):
      id="code%s"%k
      v=http_counters[k]
      printer(id,v)


      
      
      
      #if is_config:
        #print_config(title,mode,group,LABELS[mode])

      
    
    
  
  
  









