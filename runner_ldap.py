#!/usr/bin/python

#This is a worker caller and it is used to get parameters from filename
#Call it using a symbolic link: runner_ldap_title_group_file.log.py

import os
import sys

def getparams():
  script_name=__file__.split('/')[-1][:-3]
  full_path=os.path.realpath(__file__)
  real_name=full_path.split('/')[-1][:-3]
  parts=script_name.replace(real_name+'_','').split('_')
  title=parts[0]
  group=parts[1]
  return full_path.replace('runner','worker'),title,title,''

params=getparams()

if len(sys.argv)>1 and sys.argv[1]=='config':
  lp=list(params)[:-1]
  row="%s config"%" ".join(lp)
else:
  row=" ".join(params)

os.system(row)
