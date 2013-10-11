#!/usr/bin/python2.7

# use at least 2.7 because Counter is not in previous versions

import re
import sys
import os

sys.path.append("..")

from utils import RowParser
from utils import get_short_agent
from etc.env import NGINX_LOGS

log_regex=r'(.*)access\.log$'
agents={}

for file in os.listdir(NGINX_LOGS):
  if re.match(log_regex,file):
    print 'Processing: %s' % file
    for i in open('/'.join((NGINX_LOGS,file)),'r'):
      try:
        datas=RowParser(i)
      except:
        print '\t wrong signature in row: %s' % i
      else:
        agent=datas.get_agent()
        if agent is not None and 'bot' in agent:
          short=get_short_agent(agent)
          sites=agents.get((agent,short),set())
          sites.add(file)
          agents[(agent,short)]=sites

for sig,sites in agents.items():
  agent,short=sig
  print "SIGN: %s"%short
  print agent
  for site in sites:
    print "\t%s"%site
  print "\n"
