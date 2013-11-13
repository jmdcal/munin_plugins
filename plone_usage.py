#!/usr/bin/python2.7

# Usage plone_usage.py [config]

import os
import sys
import psutil
from collections import deque

from utils import *

from etc.env import PLONE_GRAPHS
from etc.env import PLONE_GRAPHS_ORDER
from etc.env import INSTANCES_CACHE
from etc.env import AREASTACK_SENSORS

#Converters
def identity(x):
  res=x
  if x is None:
    res=0 
  return res

def split_counters(vals):
  try:
    rb=vals.read_bytes
    wb=vals.write_bytes
  except AttributeError:
    rb=0
    wb=0
  return {'read':rb, 'write':wb}

def get_swap(vals):
  try:
    res=sum(i.swap for i in vals)
  except TypeError:
    res=0
  return res

def get_cpu_usage(vals):
  try:
    res=sum(vals)
  except TypeError:
    res=0  
  return res 
  
def get_threads_usage(vals):    
  try:
    res=[('%s'%thr.id,thr.system_time+thr.user_time) for thr in sorted(vals)]
  except TypeError:
    res=[]
  return dict(res)

def cut(val):
  parts=val.split('/')
  res='undefined'
  if len(parts)>0:
    res=parts[-1].replace('.','_')
  return res
  
def get_storages(vals):
  try:
    res=[(cut(i.path),os.path.getsize(i.path)) for i in vals if not re.match('^(.*)\.lock$',i.path)]
  except TypeError:
    res=[]
  return dict(res) 

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

for field_name in PLONE_GRAPHS_ORDER:
  try:
    label,conv,mthd_name,cache_file=PLONE_GRAPHS[field_name]
  except KeyError:
    pass
  else:
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
          
    for s,pd in ps_cache.items():
      mthd=getattr(pd,mthd_name,None)
      if mthd is not None:      
        val=mthd()
      else:
        val=0

      try:
        fun=eval(conv)        
        val=fun(val)
      except NameError:
        #this wrap not existing conv
        val=0
      except TypeError:
        #this wrap if fun is None and fun is not applicable to val
        val=0
                      
      if isinstance(val,dict):
        for k,v in sorted(val.items()):
          id="%s_%s_%s"%(s,field_name,k)
          printer(id=id,
                  value=diff_limit(v,previous_values[id]),
                  label="%s %s"%(s,k),
                  draw=graph)
          previous_values[id]=v
      elif isinstance(val,int) or isinstance(val,float):
        id="%s_%s"%(s,field_name)
        printer(id=id,
                value=diff_limit(val,previous_values[id]),
                label=s,
                draw=graph)
        previous_values[id]=val
    if not is_config:
      previous_values.store_in_cache()
  
ps_cache.store_in_cache()


