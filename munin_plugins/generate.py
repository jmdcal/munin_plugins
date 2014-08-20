#!/usr/bin/python2.7

"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'


import subprocess
import re

from os import listdir
from os.path import exists
 
from munin_plugins import checks
from munin_plugins import plugins

def main(argv=None, **kw):  
  #We searching checkers in checks folder
  for file in sorted(listdir(checks.__path__[0])):    
    mtc=re.match('(.*)\.py$',file)    
    if mtc is not None and mtc.group(1)!='__init__':
      try:
        checker=getattr(__import__('munin_plugins.checks.%s'%mtc.group(1),globals(),locals(),['check'],-1),'check')
        checker(log,err)
      except (KeyError,ImportError) as e:        
        pass

  #Searching munin config folder    
  m_plugins,m_plugins_c=get_munin_base()
  
  #We searching plugins in plugins folder
  for file in sorted(listdir(plugins.__path__[0])):    
    mtc=re.match('^snsr_(.*)\.py$',file)    
    if mtc is not None:
      try:
        name=mtc.group(1)
        namec=name.capitalize()
        plugin=getattr(__import__('munin_plugins.plugins.snsr_%s'%name,globals(),locals(),[namec],-1),namec)
        plugin().install(m_plugins,m_plugins_c,log,err)
      except (KeyError,ImportError) as e:        
        pass
    
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

