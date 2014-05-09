#!/usr/bin/python2.7

import sys
import subprocess
from collections import Counter

from .env import REPMGR_CONF
from .env import REPMGR_STATES
from .utils import check_config

def print_config(title,group,vals):
  print 'graph_title %s' % title
  print 'graph_args --base 1000'
  print 'graph_vlabel status'
  print "graph_category %s"%group
  for id,lab,col in vals:
    print "%s.label %s" %(id,lab)
    print "%s.draw AREASTACK"%id
    print "%s.colour %s"%(id,col)
      
def main(argv=None, **kw):   
  if check_config(argv):
    print_config('Repmgr status',"repmgr",REPMGR_STATES)
  else: 
    counters=Counter()
    for id,lab,col in REPMGR_STATES:
      counters[id]=0
    try:
      out=subprocess.check_output(["repmgr","cluster","show","-f",REPMGR_CONF],stderr=subprocess.STDOUT)
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
