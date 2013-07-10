#!/usr/bin/python2.7

# Usage: 
# worker_bots.py <title> <group> <some access log[.gz]>
# or
# worker_bots.py <title> <group> <some access log[.gz]> config

import re
import sys
import fcntl
import time

from utils import *
from etc.env import LOGS
from etc.env import LOG_REGEX
from etc.env import CACHE_BOTS
from etc.env import WL_AGENTS

from collections import Counter

def load_agents_list():
  agents=Counter()
  fd=open(CACHE_BOTS,'r')
  for i in fd:
    i=i.strip()
    if len(i)>0:
      agents[i]=0
  fd.close()
  return agents

def agents_list(access_file,limit):
  agents=load_agents_list()
  for i in open(access_file,'r'):
    try:
      datas=RowParser(i)
    except AttributeError:
      pass
    else:
      dt=datas.get_date()
      agent=datas.get_agent()
      if agent is not None and 'bot' in agent and not WL_AGENTS.search(agent) and dt>limit:
        agent=get_short_agent(agent)
        agents[agent]=1+agents[agent]
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

if len(sys.argv)>3:
  title=sys.argv[1]
  group=sys.argv[2]
  filename=sys.argv[3]

  agents=agents_list(filename,limit)
  if len(sys.argv)>4:
    if sys.argv[4]=='config':
      print_config(title,group,agents)
  else:
    print_data(agents)

locked=False
while not locked:
  try:
    fcntl.flock(CACHE_BOTS,fcntl.LOCK_EX)
  except IOError:
    time.sleep(3)
  else:
    locked=True
  
fd=open(CACHE_BOTS,'w')
for l,v in agents:
  fd.write('%s\n'%l)
fd.close()
fcntl.flock(file, fcntl.LOCK_UN)
