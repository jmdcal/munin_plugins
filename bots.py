#!/usr/bin/python2.7

# use at least 2.7 because Counter is not in previous versions

import re
import sys
import os

from utils import *

from collections import Counter

logs='/var/log/nginx/'
log_regex=r'(.*)access\.log$'

def agents_list(limit):
  whitebots=re.compile('(mod_pagespeed)')
  agents=Counter()
  for file in os.listdir(logs):
    if re.match(log_regex,file):
      for i in open('/'.join((logs,file)),'r'):
        try:
          datas=RowParser(i)
        except AttributeError:
          pass
        else:
          dt=datas.get_date()
          agent=get_short_agent(datas.get_agent())
          if 'bot' in agent and not re.search(whitebots,agent) and dt>limit:
            agents[agent]=1+agents[agent]
  return agents.most_common()

def print_config(agents):
  print "graph_title Nginx Bot:"
  print "graph_args --base 1000"
  print "graph_vlabel number of call"
  print "graph_category nginx"
  
  for l,v in agents:
    print "%s.label %s" %(l,l)
#    print "%s.draw AREASTACK"
#    print "%s.colour FF0000"
#    print "%s.warning 5"
#    print "%s.critical 10"


def print_data(agents):
  for l,v in agents:
    print "%s.value %s" %(l,v)
  
limit=getlimit()
agents=agents_list(limit)
if len(sys.argv)>1:
  print_config(agents)
else:
  print_data(agents)
