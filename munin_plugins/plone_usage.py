#!/usr/bin/python2.7

import os
import psutil
from collections import deque

from munin_plugins.utils import *

from munin_plugins.etc.env import SYSTEM_DEFAULTS
from munin_plugins.etc.env import PLONE_GRAPHS
from munin_plugins.etc.env import SYSTEM_VALUE_CACHE
from munin_plugins.etc.env import INSTANCES_CACHE
from munin_plugins.etc.env import AREASTACK_SENSORS

def get_cpu_times(sys_dff,prev,curr):
  if prev==None:
    prev=curr

  pdff=mkdiff(prev,curr)          
  return get_percent_of(pdff,sys_dff)         
        
def get_memory_percent(sys_dff,prev,curr):
  return curr
   
def get_connections(sys_dff,prev,curr):
  return len(curr)
   
def get_memory_maps(sys_dff,prev,curr):
  return sum(i.swap for i in curr)
   
def get_open_files(sys_dff,prev,curr):
  return [(cut(i.path),os.path.getsize(i.path)) for i in curr if not re.match('^(.*)\.lock$',i.path)]
   
def get_io_counters(sys_dff,prev,curr):
  if prev is None:
    prev={}
  return [(k,mkdiff(prev.get(k,0),v)) for k,v in namedtuple2dict(curr).items()]
   
def get_threads(sys_dff,prev,curr):
  curr_ids=[i.id for i in curr]
  
  if prev is None:
    prev=[namedtuple2dict(i) for i in curr]
  
  prev_dct=dict([(p['id'],p['system_time']+p['user_time']) for p in prev])
  res=deque()
  
  for c in curr:
    cv=c.user_time+c.system_time
    pv=prev_dct.get(c.id,cv)
    dff=mkdiff(pv,cv)
    if sys_dff==0:
      res.append((c.id,0))
    else:
      res.append((c.id,dff*100/sys_dff))
      
  for k,v in prev_dct.items():
    if k not in curr_ids:
      res.append((k,0))
        
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

def main(argv=None, **kw):     
  is_config=check_config(argv)
  title='Plone'
  group='plone'

  printer=print_data
  if is_config:
    printer=print_config

  sys_prev,sys_curr=load_sys(SYSTEM_DEFAULTS)  

  ps_cache=CacheDict(INSTANCES_CACHE,def_value=None)
  for pd in psutil.process_iter(): 
    name=build_sensor_name(pd.cmdline)
    #ppid>1 means that is a child: this check is useful for zeo process 
    if name is not None and pd.ppid>1:
      ps_cache[name]=pd

  def merge(main,sec,field_id):
    res={}
    if sec is not None:
      for row in sec:
        id=row.get(field_id)
        res[id]=row
    if main is not None:
      for row in main:
        id=row.get(field_id)
        res[id]=row

    return res.values()


  for id,(label,cache,sys_id,mthd) in PLONE_GRAPHS.items():
    sys_dff=mkdiff(sys_prev[sys_id],sys_curr[sys_id])   
    pcache=CachePickle(cache)
    
    print "multigraph plone_%s"%id
    if is_config:
      print "graph_title %s %s"%(title,label)    
      print "graph_args --base 1000"
      print "graph_vlabel %s"%label
      print "graph_category %s"%group
      
    graph=None
    if id in AREASTACK_SENSORS: 
      graph="AREASTACK"
      
    for name,pd in ps_cache.items():  
      ids="%s_%s"%(name,id)
      curr_value=getattr(pd,mthd,lambda : None)()    
      prev_value=pcache.get(name,None)
      converter=eval(mthd)
      res=converter(sys_dff,prev_value,curr_value)

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
          
      if isinstance(curr_value,list):
        pcache[name]=merge([namedtuple2dict(cv) for cv in curr_value],prev_value,'id')
      else:
        pcache[name]=namedtuple2dict(curr_value)  

      ##Update
      if not is_config:
        ##values are saved only if the call is not (as sys_prev)
        pcache.store_in_cache()
      
  if not is_config:    
    #align prev with curr
    for k,v in sys_curr.items():    
      sys_prev[k]=v
    #store in the file
    sys_prev.store_in_cache(clean=True)
        
