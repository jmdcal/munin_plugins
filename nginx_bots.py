#!/usr/bin/python2.7

import re
import sys
import time

from utils import *
from etc.env import CACHE_BOTS
from etc.env import WL_AGENTS

def agents_list(access_file,limit):
  agents=CacheCounter(CACHE_BOTS)
  for i in open(access_file,'r'):
    try:
      datas=RowParser(i)
    except AttributeError:
      pass
    else:
      if datas.is_valid_line([200,]):
        dt=datas.get_date()
        agent=datas.get_agent()
        if agent is not None and ('bot' in agent or 'spider' in agent) and not WL_AGENTS.search(agent) and dt>limit:
          agent=get_short_agent(agent)
          agents[agent]=1+agents[agent]
  
  agents.store_in_cache()
  
  return agents.most_common()

def print_config(title,group,agents):
  print "graph_title Nginx Bots: %s"%title
  print "graph_args --base 1000"
  print "graph_vlabel number of call"
  print "graph_category %s"%group

  for l,v in agents:
    print "%s.label %s" %(l,l)
    print "%s.warning 10" %l
    print "%s.critical 30" %l
  
def print_data(agents):
  for l,v in agents:
    print "%s.value %s" %(l,v)

limit=getlimit()

title,group,filename=getparams_from_config(__file__)

if filename None:
  sys.stderr.write('Not configured: see documentation')
else:
  agents=agents_list(filename,limit)
  if len(sys.argv)>1:
    if sys.argv[1]=='config':
      print_config(title,group,agents)
  else:
    print_data(agents)


