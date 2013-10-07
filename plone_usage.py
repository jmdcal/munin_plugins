#!/usr/bin/python2.7

# Usage plone_usage.py [config]

import sys
import psutil
from collections import deque

from utils import *

from etc.env import PLONE_GRAPHS
from etc.env import INSTANCES_CACHE
from etc.env import AREASTACK_SENSORS

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
      name=name.replace('.','_')
      
  return name
  
ps_cache=CacheDict(INSTANCES_CACHE)
ps_cache.set_default(None)
#ps_cache: cmd -> (graph_id -> value)
for pd in psutil.process_iter(): 
  name=build_sensor_name(pd.cmdline)
  #ppid>1 means that 
  if name is not None and pd.ppid>1:
    ps_cache[name]=pd

is_config=(len(sys.argv)>1 and sys.argv[1]=='config')
title='Plone instances'
group='plone'

def print_data(id,v,fname):
  print "%s.value %s"%(id,v)
  
def print_config(id,v,fname):
  print "%s.label %s"%(id,id)
  if fname in AREASTACK_SENSORS: 
    print "%s.draw AREASTACK"%id

printer=print_data
if is_config:
  printer=print_config

for field_name,(label,conv,mthd_name) in PLONE_GRAPHS.items():    
  print "multigraph plone_%s"%field_name
  if is_config:
    print "graph_title %s %s"%(title,label)    
    print "graph_args --base 1000"
    print "graph_vlabel usage %s"%label
    print "graph_category %s"%group
    
  for s,pd in ps_cache.items():
    fun=eval(conv)
    mthd=getattr(pd,mthd_name,None)
    if mthd is not None:      
      val=fun(mthd())
    else:
      val=0
    if isinstance(val,dict):
      for k,v in val.items():
        id="%s_%s_%s"%(s,field_name,k)
        printer(id,v,field_name)
    else:
      id="%s_%s"%(s,field_name)
      printer(id,val,field_name)

field_name='swap'
print "multigraph plone_%s"%field_name
if is_config:
  label="Plone swap"
  print "graph_title %s %s"%(title,label)    
  print "graph_args --base 1000"
  print "graph_vlabel usage %s"%label
  print "graph_category %s"%group

for s,pd in ps_cache.items():  
  id="%s_%s"%(s,field_name)
  val=sum(i.swap for i in pd.get_memory_maps())
  printer(id,val,field_name)
      
ps_cache.store_in_cache()


