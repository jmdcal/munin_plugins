#!/usr/bin/python2.7

import sys
import subprocess
from collections import Counter

from os.path import exists

from .env import REPMGR_STATES
from .utils import check_config
from .utils import install_plugin

def print_config(title,group,vals):
  print 'graph_title %s' % title
  print 'graph_args --base 1000'
  print 'graph_vlabel status'
  print "graph_category %s"%group
  for id,lab,col in vals:
    print "%s.label %s" %(id,lab)
    print "%s.draw AREASTACK"%id
    print "%s.colour %s"%(id,col)
    
def install(plugins_dir,plug_config_dir):
  conf='/etc/nginx'
  while not exists(conf):
    conf=raw_input('Insert a valid path for repmgr config files [%s]'%conf)
  
  install_plugin('repmgr',plugins_dir,plug_config_dir,{'env.conf':conf})
    
def main(argv=None, **kw):   
  if check_config(argv):
    print_config('Repmgr status',"repmgr",REPMGR_STATES)
  else: 
    conf=os.environ.get('conf','/etc/repmgr.conf')
    
    counters=Counter()
    for id,lab,col in REPMGR_STATES:
      counters[id]=0
    try:
      out=subprocess.check_output(["repmgr","cluster","show","-f",conf],stderr=subprocess.STDOUT)
    except (subprocess.CalledProcessError, ValueError,OSError):
      #if fails means that the process is not running
      pass
    else:
      for row in out.split('\n'):
        if '|' in row:
          for id,lab,col in REPMGR_STATES:
            if lab in row:
              counters[id]+=1

    for k,v in counters.items():
      print "%s.value %s"%(k,v)

if __name__ == '__main__':
  main()
