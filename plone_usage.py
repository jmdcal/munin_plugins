#!/usr/bin/python2.7

# Usage plone_usage.py [config]

import os
import sys
import psutil
from collections import deque

from utils import *

from etc.env import PLONE_GRAPHS
from etc.env import INSTANCES_CACHE
from etc.env import AREASTACK_SENSORS
from etc.env import DERIVE_SENSORS

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

def get_swap(vals):
  return sum(i.swap for i in vals)

def get_cpu_usage(vals):
  return sum(vals)
  
def get_threads_usage(vals):    
  res=[('%s'%pos,thr.system_time+thr.user_time) for pos,thr in enumerate(vals)]
  return dict(res)

def cut(val):
  parts=val.split('/')
  res='undefined'
  if len(parts)>0:
    res=parts[-1].replace('.','_')
  return res
  
def get_storages(vals):
  return dict([(cut(i.path),os.path.getsize(i.path)) for i in vals])

def find_cfg(command):
  cfg=None
  for i in command:
    if 'zope.conf' in i or 'zeo.conf' in i:
      cfg=i
     
  return cfg

def build_sensor_name(command):
  cfg=find_cfg(command)
  name=None
  buildout=None
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

#ps_cache: cmd -> process descriptor  
ps_cache=CacheDict(INSTANCES_CACHE,def_value=None)

for pd in psutil.process_iter(): 
  name=build_sensor_name(pd.cmdline)
  #ppid>1 means that is a child: this check is useful for zeo process 
  if name is not None and pd.ppid>1:
    ps_cache[name]=pd

is_config=(len(sys.argv)>1 and sys.argv[1]=='config')
title='Plone'
group='plone'

printer=print_data
if is_config:
  printer=print_config

for field_name,(label,conv,mthd_name,cache_file) in PLONE_GRAPHS.items():    
  previous_values=CacheNumbers(cache_file)
  print "multigraph plone_%s"%field_name
  if is_config:
    print "graph_title %s %s"%(title,label)    
    print "graph_args --base 1000"
    print "graph_vlabel usage %s"%label
    print "graph_category %s"%group
    
  graph=None
  if field_name in AREASTACK_SENSORS: 
    graph="AREASTACK"
    
  tpe=None
  if field_name in DERIVE_SENSORS:
    tpe='DERIVE'
  
  for s,pd in ps_cache.items():
    fun=eval(conv)
    mthd=getattr(pd,mthd_name,None)
    if mthd is not None:      
      val=fun(mthd())
    else:
      val=0
    if isinstance(val,dict):
      for k,v in sorted(val.items()):
        id="%s_%s_%s"%(s,field_name,k)
          
        dff=v-previous_values[id]
        if dff<0:
          dff=0
          
        printer(id=id,
                value=dff,
                label="%s %s"%(s,k),
                draw=graph,
                type=tpe)
        previous_values[id]=v
    else:
      id="%s_%s"%(s,field_name)
      
      dff=val-previous_values[id]
      if dff<0:
        dff=0
      
      printer(id=id,
              value=dff,
              label=s,
              draw=graph,
              type=tpe)
      previous_values[id]=val
  previous_values.store_in_cache()
  
ps_cache.store_in_cache()


