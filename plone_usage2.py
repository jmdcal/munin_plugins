#!/usr/bin/python2.7

import os
import sys
import psutil
from collections import deque

from utils import *


from etc.env import SYSTEM_DEFAULTS
from etc.env import PLONE_GRAPHS
from etc.env import SYSTEM_VALUE_CACHE
from etc.env import INSTANCES_CACHE

def cpu_gen(sys_dff,prev,curr):
    pdff=mkdiff(prev,curr)          
    return get_percent_of(pdff,sys_dff)         
    


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


def load_sys(defaults):
  cpath,ctype=SYSTEM_VALUE_CACHE

  #Fetch from cache
  try:
    cclass=eval(ctype)
    system_cache=cclass(cpath)
  except NameError:
    system_cache=None
  
  for k in defaults:
    curr_sys_value=getattr(psutil,k,lambda :())()
    try:
      system_cache[k]
    except KeyError:  
      system_cache[k]=namedtuple2dict(curr_sys_value)

  return system_cache
  
sys_cache=load_sys(SYSTEM_DEFAULTS)  


def mktot(val):
  if isinstance(val,dict):
    tot=sum(val.values())  
  elif isinstance(val,tuple):
    tot=sum(val)
  elif isinstance(val,int) or isinstance(val,float):
    tot=val
  else:
    tot=0  
  return tot

def mkdiff(prev,curr):
  tot_c=mktot(curr)
  tot_p=mktot(prev)
  dff=tot_c-tot_p
  if dff<0:
    #the process/system was restart
    dff=tot_c
  return dff


is_config=(len(sys.argv)>1 and sys.argv[1]=='config')
title='Plone'
group='plone'

printer=print_data
if is_config:
  printer=print_config


ps_cache=CacheDict(INSTANCES_CACHE,def_value=None)
for pd in psutil.process_iter(): 
  name=build_sensor_name(pd.cmdline)
  #ppid>1 means that is a child: this check is useful for zeo process 
  if name is not None and pd.ppid>1:
    ps_cache[name]=pd

for id,(title,cache,sys_id,mthd) in PLONE_GRAPHS.items():
  
  graph=None
  
  curr_sys_value=getattr(psutil,sys_id,lambda : ())()
  prev_sys_value=sys_cache[sys_id]  
  sys_dff=mkdiff(prev_sys_value,curr_sys_value)
    
  pcache=CacheNumbers(cache)
  
  ## da mettere esternamente per evitare di fargli ritrovare ogni volta gli stessi processi
  #for pd in psutil.process_iter():
    #name=build_sensor_name(pd.cmdline)
    ##ppid>1 means that is a child: this check is useful for zeo process 
    #if name is not None and pd.ppid>1:  
      
      
  for name,pd in ps_cache.items():  
   
    id="%s_%s"%(name,id)
    
    
    curr_value=getattr(pd,mthd,lambda :())()
    try:
      prev_value=pcache[name]
    except KeyError:
      pcache[name]=prev_value=namedtuple2dict(curr_value)

    res=cpu_gen(sys_dff,prev_value,curr_value)

    if isinstance(res,int) or isinstance(res,float):
      printer(id=id,
              value=res,
              label=name,
              draw=graph)
      
    pcache[name]=namedtuple2dict(curr_value)
    
    
  
  
  #Update
  if not is_config:
    #values are saved only if the call is not (as sys_cache)
    pcache.store_in_cache()
  
  sys_cache[sys_id]=namedtuple2dict(curr_sys_value)

  
#Save
if not is_config:
  #sys values are saved only if the call is not 
  sys_cache.store_in_cache()
  
ps_cache.store_in_cache()





        
        
        
    
    
        
    
    
    
    



