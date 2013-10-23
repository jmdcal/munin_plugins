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
  id='latencyaggregator'
  
  def __init__(self,title,group):
    self.title=title
    self.group=group
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
        self.counter[idx]=1+self.counter[idx]
      else:
        self.counter['others']=1+self.counter['others']
        
  def print_config_header(self):
    print "graph_title Nginx latency: %s"%self.title
    print "graph_args --base 1000"
    print "graph_vlabel number of pages"
    print "graph_category %s"%self.group
    
  def print_data(self, printer):
    for threshould in INTERVALS:
      id="numbers%s"%str(threshould).replace('.','')
      v=self.counter[str(threshould)]            
      printer(id,v)

    id="numbersother"
    v=self.counter['others']            
    printer(id,v)
        
  def update_cache(self):
    pass
        
class BotsCounter(object):
  id='botscounter'
  
  def __init__(self,title,group):
    self.title=title
    self.group=group
    self.counter=CacheCounter(CACHE_BOTS)
    
  def update_with(self,datas):    
    if datas.get_int_code() in [200,]:
      agent=datas.get_agent()
      agent=get_short_agent(agent)
      self.counter[agent]=1+self.counter[agent]
      
  def print_config_header(self):
    print "graph_title Nginx Bots: %s"%self.title
    print "graph_args --base 1000"
    print "graph_vlabel number of call"
    print "graph_category %s"%self.group

  def print_data(self, printer):
    for l,v in self.counter.items():
      printer(l,v)

  def update_cache(self):
    self.counter.store_in_cache()
     
class HttpCodesCounter(object):
  id='httpcodescounter'
  
  def __init__(self,title,group):
    self.title=title
    self.group=group
    self.counter=Counter(dict([(str(i),0) for i in HTTP_CODES.keys()]))
    
  def update_with(self,datas):
    if datas.get_int_code() in HTTP_CODES.keys():
      code=datas.get_code()
      self.counter[code]=self.counter[code]+1
          
  def print_config_header(self):    
    print "graph_title Nginx http codes: %s"%self.title
    print "graph_args --base 1000"
    print "graph_vlabel q.ty"
    print "graph_category %s"%self.group
    
  def print_data(self, printer):
    for k in sorted(HTTP_CODES.keys()):      
      printer("code%s"%k,self.counter[str(k)])

  def update_cache(self):
    pass
     
is_config=(len(sys.argv)>1 and sys.argv[1]=='config')
files=getparams_from_config()

limit=getlimit()

printer=print_data
if is_config:
  printer=print_config

analyzers=(LatencyAggregator,BotsCounter,HttpCodesCounter)

if len(files)<1:
  sys.stderr.write('Not configured: see documentation')
else:     
  for title,group,filename in files:
    #creates a list of analyzers
    an_objs=[cl(title,group) for cl in analyzers]
               
    #read from files valid rows
    fi=open(filename,'r')
    for row in fi:
      datas=RowParser(row)
      if datas.get_date()>limit:                      
        for an in an_objs:
           an.update_with(datas)

    fi.close()
  
    #prints
    for an in an_objs:
      print "multigraph nginx_%s_%s"%(an.id,filename.replace('/','_').replace('.','_'))
      if is_config:
        an.print_config_header()    
      an.print_data(printer)
      an.update_cache()
      
  
  
  









