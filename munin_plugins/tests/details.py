#!/usr/bin/python2.7

# use at least 2.7 because Counter is not in previous versions

import re
import sys
import os

from base64 import b16decode

if len(sys.argv)>1:
  parts=sys.argv[1].split('_')
  parts[2]=b16decode(parts[2])
  parts[4]=b16decode(parts[4])
  print parts
  
else:
  print "Usage: dateails.py runner_aggr_xxxxxxxxxxx_nginx_xxxxxxx"
  