#!/usr/bin/python2.7

# use at least 2.7 because Counter is not in previous versions

import re
import sys
import os

from utils import *

from ..etc.env import LOGS

log_regex=r'(.*)access\.log$'

for file in os.listdir(LOGS):
  if re.match(log_regex,file):
    print 'Processing: %s' % file
    for i in open('/'.join((logs,file)),'r'):
      try:
        datas=RowParser(i)
      except:
        print '\t wrong signature in row: %s' % i
      else:
        print "\t found %s" % datas.get_agent()