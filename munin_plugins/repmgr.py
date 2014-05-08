#!/usr/bin/python2.7

import sys
import subprocess
from collections import Counter

states=[('failed','FAILED','FF0000'),('master','master','00FF00'),('standby','standby','FFFF00')]

def main(argv=None, **kw): 
  
  if len(sys.argv)>1 and sys.argv[1]=='config':
    print 'graph_title Repmgr status'
    print 'graph_args --base 1000'
    print 'graph_vlabel status'
    print 'graph_category Repmgr'
    for id,lab,col in states:
      print "%s.label %s" %(id,lab)
      print "%s.draw AREASTACK"%id
      print "%s.colour %s"%(id,col)

    
  else: 
    counters=Counter()
    for id,lab,col in states:
      counters[id]=0
    
    out=subprocess.check_output(["repmgr","cluster","show","-f","/etc/repmgr/repmgr.conf"],stderr=subprocess.STDOUT)

    for row in out.split('\n'):
      if '|' in row:
        for id,lab,col in states:
          if lab in row:
            counters[id]+=1

    for k,v in counters.items():
      print "%s.value %s"%(k,v)

if __name__ == '__main__':
  main()
