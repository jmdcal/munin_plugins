#!/usr/bin/python2.7

import re  

import fcntl
import time
import subprocess

from munin_plugins.utils import *
from munin_plugins.etc.env import MONIT_STATUS
from munin_plugins.etc.env import MONIT_FIRSTS
from munin_plugins.etc.env import MONIT_LASTESTS
from munin_plugins.etc.env import MONIT_PARSER
from munin_plugins.etc.env import MONIT_PERCENTAGE_GRAPH
from munin_plugins.etc.env import MONIT_FULL
from munin_plugins.etc.env import MONIT_OPTS
from munin_plugins.etc.env import CACHE_MONIT

def graph_order(alls,pre,post):
  to_exclude=pre+post
  middle=[i for i in alls if i not in to_exclude]  
  return [i.strip().replace(' ','_') for i in  pre+middle+post]

def print_config(title,group,vals):
  print "graph_title %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel status"
  print "graph_category %s"%group
  print "graph_order %s" % " ".join(graph_order(vals,MONIT_FIRSTS,MONIT_LASTESTS))
  for l in vals:
    #get color if available
    c=MONIT_STATUS.get(l,None)
    id=l.strip().replace(' ','_')
    print "%s.label %s" % (id,l)
    print "%s.draw AREASTACK" % id
    if c is not None:
      print "%s.colour %s"  % (id,c)
    
def parse_monit_row(row):
  status=None
  try:
    groups=MONIT_PARSER.match(row).groups()
  except AttributeError:
    pass
  else:
    status=groups[2].lower().strip()
  return status

def main(argv=None, **kw): 
  #We init at least with failedtest counter
  to_init=['monit down',]
  if MONIT_FULL:
    to_init+=MONIT_STATUS.keys()

  counts=CacheCounter(CACHE_MONIT)
  for i in to_init:
    counts[i]=0

  if check_config(argv):
    print_config('Monit status','monit',counts.keys())
  else:  
    csensors=1
    try:
      pid=int(subprocess.check_output(['pidof','monit'],stderr=subprocess.STDOUT).strip())
    except (subprocess.CalledProcessError, ValueError):
      #if fails means that the process is not running
      counts['monit down']=1
    else:
      csensors=0
      sensors=subprocess.check_output(['monit','summary']+MONIT_OPTS,stderr=subprocess.STDOUT)
      for row in sensors.split('\n'):
        status=parse_monit_row(row)
        if status is not None:
          counts[status]=counts[status]+1
          csensors+=1

    norm=lambda x:x
    if MONIT_PERCENTAGE_GRAPH:
      norm=lambda x:(x*100/csensors)
      
    for l,v in counts.items():
      id=l.replace(' ','_')
      print "%s.value %s"% (id,norm(v))
        
  counts.store_in_cache()
    
if __name__ == '__main__':
  main()
