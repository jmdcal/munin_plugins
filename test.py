#!/usr/bin/python2.7

# use at least 2.7 because Counter is not in previous versions

import re
import sys
import os

from utils import *

logs='/var/log/nginx/'
log_regex=r'(.*)access\.log$'

for file in os.listdir(logs):
  if re.match(log_regex,file):
    for i in open('/'.join((logs,file)),'r'):
      try:
        datas=RowParser(i)
      except:
        print '--> %s' % file
        print '--> %s' % i
        import pdb; pdb.set_trace()
