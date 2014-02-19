#!/usr/bin/python2.7

import os
import psutil
from collections import deque

from munin_plugins.utils import *

from munin_plugins.etc.env import SYSTEM_DEFAULTS
from munin_plugins.etc.env import SYSTEM_VALUE_CACHE
from munin_plugins.etc.env import INSTANCES_CACHE

from munin_plugins.plone_analyzers import cpu_usage_snsr
from munin_plugins.plone_analyzers import memory_snsr
from munin_plugins.plone_analyzers import connections_snsr
from munin_plugins.plone_analyzers import swap_snsr
from munin_plugins.plone_analyzers import storages_snsr
from munin_plugins.plone_analyzers import io_counters_snsr
from munin_plugins.plone_analyzers import threads_snsr

def load_sys(defaults):
  cpath,ctype=SYSTEM_VALUE_CACHE

  #Fetch from cache
  try:
    cclass=eval(ctype)
    system_cache=cclass(cpath)
  except NameError:
    system_cache=None
  sys_curr={}
  
  for k in defaults:
    sys_curr[k]=namedtuple2dict(getattr(psutil,k,lambda : None)())
    try:
      system_cache[k]
    except KeyError:  
      system_cache[k]=sys_curr[k]

  return system_cache,sys_curr
  
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


def load_process():
  cache=CacheDict(INSTANCES_CACHE,def_value=None)
  for pd in psutil.process_iter(): 
    name=build_sensor_name(pd.cmdline)
    #ppid>1 means that is a child: this check is useful for zeo process 
    if name is not None and pd.ppid>1:
      cache[name]=pd
  return cache


def main(argv=None, **kw):     
  is_config=check_config(argv)
  title='Plone'
  group='plone'

  printer=print_data
  if is_config:
    printer=print_config

  sys_prev,sys_curr=load_sys(SYSTEM_DEFAULTS)  
  ps_cache=load_process()
  analyzer_classes=(cpu_usage_snsr,memory_snsr,connections_snsr,swap_snsr,storages_snsr,io_counters_snsr,threads_snsr)
  
  for cl in analyzer_classes:
    sensor=cl(sys_prev,sys_curr)

    print "multigraph plone_%s"%cl.__name__
    if is_config:
      print "graph_title %s %s"%(title,sensor.label)    
      print "graph_args --base 1000"
      print "graph_vlabel %s"%sensor.label
      print "graph_category %s"%group
    
    graph=sensor.graphType()
    for name,pd in ps_cache.items():  
      ids="%s_%s"%(name,cl.__name__)
      curr_value=getattr(pd,sensor.proc_mtd,lambda : None)()    
      prev_value=sensor.getValue(name)
      
      res=sensor.calculate(name,curr_value)

      if isinstance(res,int) or isinstance(res,float):
        printer(id=ids,
                value=res,
                label=name,
                draw=graph)
      elif isinstance(res,list) or isinstance(res,deque):
        for fd,row in res:
          printer(id='%s-%s'%(ids,fd),
                  value=row,
                  label='%s %s '%(name,fd),
                  draw=graph)
      
    if not is_config:        
      sensor.store_in_cache()

  if not is_config:    
    #align prev with curr
    for k,v in sys_curr.items():    
      sys_prev[k]=v
    #store in the file
    sys_prev.store_in_cache(clean=True)


