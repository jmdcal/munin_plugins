#!/usr/bin/python2.7

import subprocess

import sys

from os import makedirs
from os.path import exists
from os.path import join

from .env import SYS_VAR_PATH

def main(argv=None, **kw):  
  check_python()
  check_psutil()
  check_cache()
  
  m_plugins,m_plugins_c=get_munin_base()
    
  #apache
  from apache import Apache
  Apache().install(m_plugins,m_plugins_c)
  
  #nginx_full
  from nginx_full import Nginx
  Nginx().install(m_plugins,m_plugins_c)
 
  #plone_usage
  from plone_usage import Plone
  Plone().install(m_plugins,m_plugins_c)
  
  #monit_downtime
  from monit_downtime import Monit
  Monit().install(m_plugins,m_plugins_c)
  
  #repmgr
  from .repmgr import Repmgr
  Repmgr().install(m_plugins,m_plugins_c)
  
  #java
  #suspended temporally
  
def err(msg):
  print "ERROR: %s"%msg

def log(msg):
  print msg
  
def check_python():  
  vers=sys.version_info
  if vers<(2,7):
    err("Python version is not valid (required 2.7.x)")
  else:
    log("Python is ok [%s.%s.%s %s-%s]"%(vers.major,vers.minor,vers.micro,vers.releaselevel,vers.serial))
  
def check_psutil():
  try: 
    import psutil
    log("Psutil is ok [%s.%s.%s]"%psutil.version_info)
  except ImportError:
    err("Unable import psutil")

def check_cache():  
  dest=join(SYS_VAR_PATH,'cache')
  if not exists(dest):
    makedirs(dest) 
    print "Cache is ok (created) [%s]"%dest
  else:
    print "Cache is ok [%s]"%dest

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

