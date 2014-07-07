#!/usr/bin/python2.7

import os
import psutil
from collections import deque

from .utils import *
from .env import SYSTEM_DEFAULTS
from .env import SYSTEM_VALUE_CACHE
from .env import JAVA_INSTANCES_CACHE
from .java_analyzers import cpu_usage_snsr
from .java_analyzers import memory_snsr
from .java_analyzers import connections_snsr
from .java_analyzers import swap_snsr
from .java_analyzers import storages_snsr
from .java_analyzers import io_counters_snsr
from .java_analyzers import io_counters_abs_snsr
from .java_analyzers import threads_snsr

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
  
def build_sensor_name(command):
  name=None
  if 'bin/java' in command:
    if 'Bootstrap' in command:
      name='catalina.startup.Bootstrap'
    elif 'org.jboss.Main' in command:
      name='org.jboss.Main'
  
  return name


def load_process():
  cache=CacheDict(JAVA_INSTANCES_CACHE,def_value=None)
  for pd in psutil.process_iter(): 
    name=build_sensor_name(pd.cmdline())
    #ppid>1 means that is a child: this check is useful for zeo process 
    if name is not None and pd.ppid>1:
      cache[name]=pd
  return cache


def main(argv=None, **kw):     
  is_config=check_config(argv)
  title='Java'
  group='java'

  printer=print_data
  if is_config:
    printer=print_config

  sys_prev,sys_curr=load_sys(SYSTEM_DEFAULTS)  
  ps_cache=load_process()
  analyzer_classes=(cpu_usage_snsr,memory_snsr,connections_snsr,swap_snsr,storages_snsr,io_counters_snsr,io_counters_abs_snsr,threads_snsr)
  
  for cl in analyzer_classes:
    sensor=cl(sys_prev,sys_curr)

    print "multigraph java_%s"%cl.__name__
    if is_config:
      print "graph_title %s %s"%(title,sensor.label)    
      print "graph_args --base 1000"
      print "graph_vlabel %s"%sensor.label
      print "graph_category %s"%group
    
    graph=sensor.graphType()
    for name,pd in ps_cache.items():  
      ids="%s_%s"%(name,cl.__name__)
      curr_value=getattr(pd,sensor.proc_mtd,lambda : None)()    
      
      res=sensor.calculate(name,curr_value)

      if isinstance(res,int) or isinstance(res,float):
        printer(id=ids,
                value=res,
                label=name,
                draw=graph)
      elif isinstance(res,list) or isinstance(res,deque) or isinstance(res,set):
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
    sys_prev.store_in_cache()
    ps_cache.store_in_cache();
