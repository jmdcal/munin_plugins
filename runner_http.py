#!/usr/bin/python

#This is a worker caller and it is used to get parameters from filename
#Call it using a symbolic link: runner_http_title_group_file.log.py

import os
import sys
from etc.env import logs
from utils import getparam()

params=getparams(__file__)

if len(sys.argv)>1 and sys.argv[1]=='config':
  lp=list(params)[:-1]
  row="%s config"%" ".join(lp)
else:
  row=" ".join(params)

os.system(row)
