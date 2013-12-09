#!/usr/bin/python2.7

# Usage plone_usage.py [config]

import os
import sys
import psutil
from collections import deque

from utils import *

from etc.env import MINUTES
from etc.env import PLONE_GRAPHS
from etc.env import PLONE_GRAPHS_ORDER
from etc.env import INSTANCES_CACHE
from etc.env import AREASTACK_SENSORS
from etc.env import SYSTEM_VALUE_CACHE


#Converters
def identity(x,prevs,env):
  res=x
  if x is None:
    res=0 
  return res,None

def get_cpu_usage(vals,prevs,env):
  #env['system_usage_prev'] is a dict
  #env['system_usage_curr'] is a namedtuple
  fd=open('/tmp/debug_plone_usage.log','w+')
  fd.write('================================')
  
  sys_u=sum(env['system_usage_curr'])-sum(env['system_usage_prev'].values())  
  fd.write('sys_u %s'%sys_u)  
  try:
    act=dict(user=vals.user,sys=vals.system)
  except AttributeError:    
    act=dict(user=0,sys=0)
  fd.write('act %s'%act)
  #if previous is None means there's no difference we can do so is 0
  proc_u=0
  if prevs is not None:
    proc_u=sum(act.values())-sum(prevs.values())
  
  fd.write('proc_u %s'%proc_u)
  
  perc=get_percent_of(proc_u,sys_u)
  
  fd.write('perc %s'%perc)
  fd.close()
  return perc,act

def get_threads_usage(vals,prevs,env):
  #env['system_usage_prev'] is a dict
  #env['system_usage_curr'] is a namedtuple
  sys_u=sum(env['system_usage_curr'])-sum(env['system_usage_prev'].values())

  try:
    act=dict([('%s'%thr.id,thr.system_time+thr.user_time) for thr in sorted(vals)])
  except TypeError:
    act={}
  if prevs is not None:
    dff=dict([(k,get_percent_of(fnz(v-prevs.get(k,0)),sys_u)) for k,v in act.items()])
  else:
    #if previous is None means there's no difference we can do so is 0
    dff=dict([(k,0) for k,v in act.items()])  
  return dff,act

def get_swap(vals,prevs,env):
  try:
    res=sum(i.swap for i in vals)
  except TypeError:
    res=0
  return res,None

def get_storages(vals,prevs,env):
  try:
    res=[(cut(i.path),os.path.getsize(i.path)) for i in vals if not re.match('^(.*)\.lock$',i.path)]
  except TypeError:
    res=[]
  return dict(res),None 

def split_counters(vals,prevs,env):
  try:
    rb=vals.read_bytes
    wb=vals.write_bytes
  except AttributeError:
    rb=0
    wb=0
  act={'read':rb, 'write':wb}
  dff=act
  if prevs is not None:
    dff=dict([(k,fnz(v-prevs.get(k,0))) for k,v in act.items()])
  else:
    #if previous is None means there's no difference we can do so is 0
    dff=dict([(k,0) for k,v in act.items()])
  return dff,act

def get_size(vals,prevs,env):
  return len(vals),None

def fnz(val):
  res=round(val,2)
  #This fix -0.0 numbers
  if res==0.0:
    res=0.0
       
  return res

def cut(val):
  parts=val.split('/')
  res='undefined'
  if len(parts)>0:
    res=parts[-1].replace('.','_')
  return res
 
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


def load_env():
  cpath,ctype=SYSTEM_VALUE_CACHE
  env={}
  try:
    cclass=eval(ctype)
    system_cache=cclass(cpath)
    env['system_usage_prev']=system_cache['cpu_times']
  except NameError:
    system_cache=None
    env['system_usage_prev']=namedtuple2dict(psutil.cpu_times())
  except KeyError:
    env['system_usage_prev']=namedtuple2dict(psutil.cpu_times())
    
  env['system_usage_curr']=psutil.cpu_times()
  system_cache['cpu_times']=env['system_usage_curr']
  
  return env,system_cache

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

env,system_cache=load_env()

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
      print "graph_vlabel %s"%label
      print "graph_category %s"%group
      
    graph=None
    if field_name in AREASTACK_SENSORS: 
      graph="AREASTACK"
          
    for s,pd in ps_cache.items():
      id="%s_%s"%(s,field_name)
      mthd=getattr(pd,mthd_name,None)
      if mthd is not None:      
        val=mthd()
      else:
        val=0

      try:
        fun=eval(conv)        
        val,to_store=fun(val,previous_values.get(id,None),env)
      except NameError:
        #this wrap not existing conv
        val=0
        to_store=None
      except TypeError:
        #this wrap if fun is None and fun is not applicable to val
        val=0      
        to_store=None

      if isinstance(val,dict):
        for k,v in sorted(val.items()):
          printer(id='%s_%s'%(id,k),
                  value=v,
                  label="%s %s"%(s,k),
                  draw=graph)
        if to_store is not None:  
          previous_values[id]=to_store
      elif isinstance(val,int) or isinstance(val,float):        
        printer(id=id,
                value=val,
                label=s,
                draw=graph)
        if to_store is not None:  
          previous_values[id]=to_store
          
    if not is_config:
      previous_values.store_in_cache()
  
ps_cache.store_in_cache()
if system_cache is not None:
  system_cache.store_in_cache()

