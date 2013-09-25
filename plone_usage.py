#!/usr/bin/python2.7

# Usage plone_usage.py [config]

import sys
import psutil
from collections import deque

from utils import *

from etc.env import PLONE_GRAPHS
from etc.env import ZOPE_PARSER
from etc.env import ZEO_PARSER
from etc.env import INSTANCES_CACHE

#Utils: empty process descriptor
def empty_desc():
  desc=dict([(i,None) for i in PLONE_GRAPHS.keys()])  
  return desc

#Converters
def identity(x):
  res=x
  if x is None:
    res=0 
  return res

def split_counters(vals):
  rb=0
  wb=0
  try:
    rb=vals.read_bytes
    wb=vals.write_bytes
  except AttributeError:
    pass
  return {'read':rb, 'write':wb}

def print_config(title,group,sensors):
  for field_name,(label,conv) in PLONE_GRAPHS.items():    
    print "multigraph plone_%s"%field_name
    print "graph_title %s %s"%(title,label)    
    print "graph_args --base 1000"
    print "graph_vlabel usage %s"%label
    print "graph_category %s"%group
    for s in sensors.keys():
      print "%s_%s.label %s"%(s,field_name,s)

def find_cfg(command):
  cfg=None
  for i in command:
    if 'zope.conf' in i or 'zeo.conf' in i:
      cfg=i
     
  return cfg

def build_sensor_name(command):
  cfg=find_cfg(command)
  name=None
  if cfg is not None:
    try:
      instance_num=re.search('parts/(.*?)/etc',cfg).group(1)
      buildout=re.search('/(.*?)/parts',cfg).group(1)
    except AttributeError:
      pass
    else:
      path=buildout.split('/')
      name=path[-1]
      if name=='buildout':
        name=path[-2]
      name='%s_%s'%(name,instance_num)
      
  return name
  

ps_cache=CacheDict(INSTANCES_CACHE)
ps_cache.set_default(empty_desc())
#ps_cache: cmd -> (graph_id -> value)
for pd in psutil.process_iter(): 
  name=build_sensor_name(pd.cmdline)
  #ppid>1 means that 
  if name is not None and pd.ppid>1:
    ps_cache[name]=pd.as_dict()

is_config=(len(sys.argv)>1 and sys.argv[1]=='config')
title='Plone instances'
group='plone'

attr='value'
to_real=lambda val,lab:val
if is_config:
  attr='label'
  to_real=lambda val,lab:lab

for field_name,(label,conv) in PLONE_GRAPHS.items():    
  if is_config:
    print "multigraph plone_%s"%field_name
    print "graph_title %s %s"%(title,label)    
    print "graph_args --base 1000"
    print "graph_vlabel usage %s"%label
    print "graph_category %s"%group
    
  for s,desc in ps_cache.items():
    fun=eval(conv)
    val=fun(desc[field_name])
    if isinstance(val,dict):
      for k,v in val.items():
        id="%s_%s_%s"%(s,field_name,k)
        print "%s.%s %s"%(id,attr,to_real(v,id))
    else:
      id="%s_%s"%(s,field_name)
      print "%s.%s %s"%(id,attr,to_real(val,id))
      
ps_cache.store_in_cache()


