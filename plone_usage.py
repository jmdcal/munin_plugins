#!/usr/bin/python2.7

# Usage plone_usage.py [config]

import sys
import psutil
from collections import deque

from utils import *

from etc.env import PS_FIELDS
from etc.env import ZOPE_ZEO_PARSER
from etc.env import INSTANCES_CACHE

def print_config(title,group,vals):
  print "graph_title %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel usage"
  print "graph_category %s"%group

  for id,l in vals:
    print "%s.label %s" % (id,l)

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

#Utils: empty process descriptor
def empty_desc():
  desc=dict([(i,None) for i in PS_FIELDS.keys()])  
  return desc

#Parser for 
def is_valid_line(row):
  cfg=None
  try:
    gr=ZOPE_ZEO_PARSER.search(row).groups()
    cfg=gr[1]
  except AttributeError:
    pass
  return cfg

def get_instance_name(cfg):
  title,conf=cfg.split('parts')
  name=conf.strip('/').split('/')[0]
  title='%sbin/%s'%(title,name)
  id=title.strip('/').replace('/','_')  
  return (title,id)


#cache is a dict cmd -> desc

ps_cache=CacheDict(INSTANCES_CACHE)
ps_cache.set_default(empty_desc())
for pd in psutil.process_iter():
  try:
    desc=pd.as_dict()
  except psutil._error.NoSuchProcess:
    cmd=''
  else:
    cmd=" ".join(desc['cmdline'])
  
  cfg=is_valid_line(cmd)
  if cfg is not None:  
    ps_cache[cmd]=desc


sensors=deque()  
values=deque()

for cmd,desc in ps_cache.items():
  #we revaluate cmd because some are taked from cache 
  cfg=is_valid_line(cmd)
  title,id=get_instance_name(cfg)
  for field_name,details in PS_FIELDS.items():
    label,conv_name=details    
    fun=eval(conv_name)
    
    try:
      val=fun(desc[field_name])
    except TypeError:
      #This trap a converter failure
      val=0      
      
    if isinstance(val,dict):
      for k,v in val.items():
        row_id='%s_%s_%s'%(id,field_name,k)
        label_ex='%s %s'%(label,k)
        values.append('%s.value %s'%(row_id,v))
        sensors.append((row_id,label_ex))
    else:
      row_id='%s_%s'%(id,field_name)
      values.append('%s.value %s'%(row_id,val))
      sensors.append((row_id,label))
      
if len(sys.argv)>1 and sys.argv[1]=='config':
  print_config('Plone instances','plone',sensors)
else:  
  for row in values:
    print row    

ps_cache.store_in_cache()