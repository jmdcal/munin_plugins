#!/usr/bin/python2.7

# Usage plone_usage.py [config]

import sys
import psutil
from collections import deque

from utils import *

from etc.env import PS_FIELDS
from etc.env import ZOPE_ZEO_PARSER


def print_config(title,group,vals):
  print "graph_title %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel usage"
  print "graph_category %s"%group

  for id,l,cfg,desc in vals:
    print "%s.label %s" % (id,l)

#Converters
identity=lambda x:x 

def split_counters(vals):
  return {'read':vals.read_bytes,
          'write':vals.write_bytes,}

#Parser for 
def is_valid_line(row):
  cfg=None
  try:
    gr=ZOPE_ZEO_PARSER.search(row).groups()
    cfg='%s%s'%(gr[0],gr[1])
  except AttributeError:
    pass
  return cfg

def get_instance_name(cfg):
  title,conf=cfg.split('parts')
  name=conf.strip('/').split('/')[0]
  title='%sbin/%s'%(title,name)
  id=title.strip('/').replace('/','_')  
  return (title,id)

plone_processes=deque()
for pd in psutil.process_iter():
  try:
    desc=pd.as_dict()
  except psutil._error.NoSuchProcess:
    cmd=''
  else:
    cmd=" ".join(desc['cmdline'])

  cfg=is_valid_line(cmd)
  if cfg is not None:    
    title,id=get_instance_name(cfg)
    plone_processes.append((id,title,cfg,desc))


if len(sys.argv)>1 and sys.argv[1]=='config':
  print_config('Plone instances','plone',plone_processes)
else:  
  for id,title,cfg,desc in plone_processes:    
    for ff,det in PS_FIELDS.items():
      ll,fun=det
      conv=eval(fun)
      val=conv(desc[ff])
      if isinstance(val,dict):
        for k,v in val.items():
          print '%s_%s_%s.value %s'%(id,ff,k,v)
      else:
        print '%s_%s.value %s'%(id,ff,val)
    
 