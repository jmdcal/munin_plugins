#!/usr/bin/python2.7

import os
import sys
import subprocess
from collections import Counter

from os.path import exists

from munin_plugins.plugins.plugin import Plugin

class Repmgr(Plugin):
  _defaults={
    'title':'Repmgr status',
    'group':'repmgr',
    'conf':'/etc/repmgr.conf',
    'repmgr_state_0': 'failed,FAILED,FF0000',
    'repmgr_state_1': 'master,master,00FF00',
    'repmgr_state_2': 'standby,standby,FFFF00',
  }
  _prefix_name='snsr_repmgr'
     
  def populate_vals(self):
    return self.getenvs('repmgr_state_')
  
  def print_config(self):
    print 'graph_title %s' % self.getenv('title')
    print 'graph_args --base 1000'
    print 'graph_vlabel status'
    print "graph_category %s"%self.getenv('group')
    for id,lab,col in self.populate_vals():
      print "%s.label %s" %(id,lab)
      print "%s.draw AREASTACK"%id
      print "%s.colour %s"%(id,col)
  
  def envvars(self):
    envvars=super(Repmgr,self).envvars()
    conf=self._defaults.get('conf','')
    while not exists(conf):
      conf=raw_input('Insert a valid path for repmgr config files [%s]'%conf)
    
    envvars['conf']=conf
    return envvars
        
  def main(self,argv=None, **kw):     
    if self.check_config(argv):
      self.print_config()
    else: 
      conf=self.getenv('conf')
      vals=self.populate_vals()
      if len(vals)==0:
        sys.stderr.write('Not configured: see documentation\n')
      else:
        counters=Counter()
        for id,lab,col in vals:
          counters[id]=0
        try:
          out=subprocess.check_output(["repmgr","cluster","show","-f",conf],stderr=subprocess.STDOUT)
        except (subprocess.CalledProcessError, ValueError,OSError):
          #if fails means that the process is not running
          pass
        else:
          for row in out.split('\n'):
            if '|' in row:
              for id,lab,col in states:
                if lab in row:
                  counters[id]+=1

        for k,v in counters.items():
          print "%s.value %s"%(k,v)


def main(argv=None, **kw):
  Repmgr().main()
  
if __name__ == '__main__':
  main()
