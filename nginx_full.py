#!/usr/bin/python2.7

import sys
from collections import Counter
from utils import *

from etc.env import CACHE_BOTS
from etc.env import INTERVALS
from etc.env import HTTP_CODES
from etc.env import COLORS
from etc.env import MINUTES


def print_data(id,v):
  print "%s.value %s"%(id,v)

def print_config(id,v):
  print "%s.label %s"%(id,id)

class LatencyAggregator(object):
  def __init__(self):
    self.counter=Counter(dict([(str(i),0) for i in INTERVALS]+[('others',0)]))
    
  def update_with(self,datas):
    lat=datas.get_latency()
     
    #aggr evaluate
    if lat is not None and datas.get_bytes()>0 and datas.get_int_code() in [200,]:
      md=ft(lat)
      pos=0
      while pos<len(INTERVALS) and INTERVALS[pos]<md:
        pos+=1

      if pos<len(INTERVALS):
        idx=str(INTERVALS[pos])
        self.counter[idx]=1+aggr_counters[idx]
      else:
        self.counter['others']=1+self.counter['others']
        
  def print_config_header(self,title,group):
    print "graph_title Nginx latency (new): %s"%title
    print "graph_args --base 1000"
    print "graph_vlabel number of pages"
    print "graph_category %s"%group
    
  def print_data(self, printer):
    for threshould in INTERVALS:
      id="numbers%s"%str(threshould).replace('.','')
      v=self.counter[str(threshould)]            
      printer(id,v)

    id="numbersother"
    v=self.counter['others']            
    printer(id,v)
        
class BotsCounter(object):
  def __init__(self):
    self.counter=CacheCounter(CACHE_BOTS)
    
  def update_with(self,datas):
    if datas.get_int_code() in [200,]:
      agent=datas.get_agent()
      agent=get_short_agent(agent)
      self.counter[agent]=1+self.counter[agent]
      
  def print_config_header(self,title,group):
    print "graph_title Nginx Bots: %s"%title
    print "graph_args --base 1000"
    print "graph_vlabel number of call"
    print "graph_category %s"%group

  def print_data(self, printer):
    for l,v in self.counter:
      printer(l,v)
     
class HttpCodesCounter(object):
  def __init__(self):
    self.counter=Counter(dict([(str(i),0) for i in HTTP_CODES.keys()]))
    
  def update_with(self,datas):
    if datas.get_int_code() in HTTP_CODES.keys():
      self.counter[code]=self.counter[code]+1
          
  def print_config_header(self,title,group):    
    print "graph_title Nginx http codes: %s"%title
    print "graph_args --base 1000"
    print "graph_vlabel q.ty"
    print "graph_category %s"%group
    
  def print_data(self, printer):
    for k in sorted(HTTP_CODES.keys()):
      printer("code%s"%k,self.counter[k])
     
is_config=(len(sys.argv)>1 and sys.argv[1]=='config')
files=getparams_from_config()
limit=getlimit()

printer=print_data
if is_config:
  printer=print_config


if len(files)<1:
  sys.stderr.write('Not configured: see documentation')
else:     
  for title,group,filename in files:
    #Aggr init
    aggr=LatencyAggregator()
    #aggr_counters=Counter(dict([(str(i),0) for i in INTERVALS]+[('others',0)]))

    #Bots init
    bots=BotsCounter()    
    
    #Http init
    httpcodes=HttpCodesCounter()
           
    #read from files valid rows
    fi=open(filename,'r')
    for row in fi:
      datas=RowParser(row)
           
      if datas.get_date()>limit:                      
        #aggr evaluate
        aggr.update_with(datas)

        #bots evaluate
        bots.update_with(datas)
          
        #http evaluate
        httpcodes.update_with(datas)
        
    #Aggr prints
    print "multigraph nginx_%s_%s"%('aggr',filename.replace('/','_').replace('.','_'))
    if is_config:
      aggr.print_config_header(title,group)    
    aggr.print_data(printer)
        
    #Bots prints
    print "multigraph nginx_%s_%s"%('bots',filename.replace('/','_').replace('.','_'))
    if is_config:
      bots.print_config_header(title,group)
    bots.print_data(printer)
          
    #Http prints
    print "multigraph nginx_%s_%s"%('http',filename.replace('/','_').replace('.','_'))
    if is_config:
      httpcodes.print_config_header(title,group)
    httpcodes.print_data(printer)


      
      
      

      
    
    
  
  
  









