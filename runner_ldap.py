#!/usr/bin/python

#This is a worker caller and it is used to get parameters from filename
#Call it using a symbolic link: runner_ldap_title_group_file.log.py

import os
import sys
from utils import getparams

params=getparams(__file__)

if len(sys.argv)>1 and sys.argv[1]=='config':
  params=params+('config',)

os.system(" ".join(params))