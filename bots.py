#!/usr/bin/python2.7

# use at least 2.7 because Counter is not in previous versions

import re
import sys
import os

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

def agents_list(limit):
  agents=load_agents_list()
  for file in os.listdir(LOGS):
    if re.match(LOG_REGEX,file):
      for i in open('/'.join((LOGS,file)),'r'):
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

def print_config(agents):
  print "graph_title Nginx Bot"
  print "graph_args --base 1000"
  print "graph_vlabel number of call"
  print "graph_category nginx"
  
  for l,v in agents:
    print "%s.label %s" %(l,l)
    print "%s.warning 10" %l
    print "%s.critical 30" %l

def print_data(agents):
  for l,v in agents:
    print "%s.value %s" %(l,v)
  
limit=getlimit()
agents=agents_list(limit)
if len(sys.argv)>1:
  print_config(agents)
else:
  print_data(agents)

fd=open(CACHE_BOTS,'w')
for l,v in agents:
  fd.write('%s\n'%l)
fd.close()
  
