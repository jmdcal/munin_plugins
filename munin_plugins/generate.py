#!/usr/bin/python2.7

import subprocess

import sys
import re

from os import listdir
from os.path import exists

from .snsr_apache import Apache
from .snsr_monit import Monit
from .snsr_nginx import Nginx
from .snsr_processes import Processes
from .snsr_repmgr import Repmgr

from .env import SYS_VAR_PATH

import checks


def main(argv=None, **kw):  

  #We searching checkers in checks folder
  for file in sorted(listdir(checks.__path__[0])):    
    mtc=re.match('(.*)\.py$',file)    
    if mtc is not None and mtc.group(1)!='__init__':
      try:
        checker=getattr(__import__('checks.%s'%mtc.group(1),globals(),locals(),['check'],-1),'check')
        checker(log,err)
      except (KeyError,ImportError) as e:        
        pass

  #Searching munin config folder    
  m_plugins,m_plugins_c=get_munin_base()
    
  Apache().install(m_plugins,m_plugins_c)
  Monit().install(m_plugins,m_plugins_c)
  Nginx().install(m_plugins,m_plugins_c)
  Processes().install(m_plugins,m_plugins_c)
  Repmgr().install(m_plugins,m_plugins_c)
    
def err(msg):
  print "ERROR: %s"%msg

def log(msg):
  print msg
 
def get_munin_base():
  expected='/etc/munin'  
  while True:
    try:
      res=subprocess.check_output(['find',expected,'-name','munin-node.conf'],stderr=subprocess.STDOUT)
      mp='%s/plugins'%expected
      mpc='%s/plugin-conf.d'%expected
      if len(res)>0 and exists(mp) and exists(mpc):
        log("Munin base config is ok [%s,%s,%s]"%(expected,mp,mpc))
        break
    except OSError:
      pass
    except subprocess.CalledProcessError, err:
      pass    
  
    new_path=''
    try:
      new_path=raw_input('Munin-node base path [%s]: '%expected)
    except SyntaxError:
      pass
  
    if len(new_path)>0:
      expected=new_path
  
  return mp,mpc

if __name__ == '__main__':
  main()

