#!/usr/bin/python2.7

# use at least 2.7 because Counter is not in previous versions

import re
import sys
import os

from utils import *

from collections import Counter

logs='/var/log/nginx'

email=re.compile("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}")
url=re.compile('http://(.*?)/')


limit=getlimit()

def reduce_sign(sign):
  uu=url.findall(sign)
  if len(uu)>0:
    sign=uu[0]
  else:
    ee=email.findall(sign)
    if len(ee)>0:
      sign=ee[0]
  return sign.split()[0].replace('.','_').replace('@','_at_')


def agents_list():
  whitebots=re.compile('(Googlebot)|(msnbot)|(bingbot)|(mod_pagespeed)')
  agents=Counter()

  for file in os.listdir(logs):
    for i in open('/'.join((logs,file)),'r'):
      res=re.findall('"(.*?)"',i)
      if len(res)>2:
        agent=res[2]
        if 'bot' in agent and not re.search(whitebots,agent):
          agents[agent]=1+agents[agent]
  
  return [(reduce_sign(s),v) for s,v in agents.most_common()]



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
  

agents=agents_list()
if len(sys.argv)>1:
  print_config(agents)
else:
  print_data(agents)
