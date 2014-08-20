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

import re  
import subprocess

from munin_plugins.plugins.plugin import Plugin
from munin_plugins.utils import CacheCounter
from munin_plugins.env import CACHE

class Monit(Plugin):
  _prefix_name='snsr_monit'
  
  @property
  def _env(self):
    inherit_env=super(Monit,self)._env
    inherit_env.update({
      'title':'Monit status',
      'group':'monit',
      'cache':"%s/monit_messages"%CACHE,
      'percentage':'True',
      'full':'False',
      'lastest':"accessible,online with all services,running,monit down",
      'line_regex':"^(Filesystem|Directory|File|Process|Remote Host|System|Fifo)\s('.*?')\s(.*)",    
      'monit_state_0':"monit down,757575",
      'monit_state_1':"running,005000",
      'monit_state_2':"online with all services,006000",
      'monit_state_3':"accessible,007000",  
      'monit_state_4':"monitored,008000",
      'monit_state_5':"initializing,009000",
      'monit_state_6':"action done,00A000", 
      'monit_state_7':"checksum succeeded,00FF00",
      'monit_state_8':"connection succeeded,00FF00",
      'monit_state_9':"content succeeded,00FF00",
      'monit_state_10':"data access succeeded,00FF00",
      'monit_state_11':"execution succeeded,00FF00",
      'monit_state_12':"filesystem flags succeeded,00FF00",
      'monit_state_13':"gid succeeded,00FF00",
      'monit_state_14':"icmp succeeded,00FF00",
      'monit_state_15':"monit instance changed not,00FF00",
      'monit_state_16':"type succeeded,00FF00",
      'monit_state_17':"exists,FFFF00",
      'monit_state_18':"permission succeeded,00FF00",
      'monit_state_19':"pid succeeded,00FF00",
      'monit_state_20':"ppid succeeded,00FF00",
      'monit_state_21':"resource limit succeeded,00FF00",
      'monit_state_22':"size succeeded,00FF00",
      'monit_state_23':"timeout recovery,FFFF00",
      'monit_state_24':"timestamp succeeded,00FF00",
      'monit_state_25':"uid succeeded,00FF00",
      'monit_state_26':"not monitored,00FFFF",
      'monit_state_27':"checksum failed,FF0000",
      'monit_state_28':"connection failed,0000FF",
      'monit_state_29':"content failed,FF0000",
      'monit_state_30':"data access error,FF0000",
      'monit_state_31':"execution failed,FF0000",
      'monit_state_32':"filesystem flags failed,FF0000",
      'monit_state_33':"gid failed,FF0000",
      'monit_state_34':"icmp failed,FF00FF",
      'monit_state_35':"monit instance changed,FF0000",
      'monit_state_36':"invalid type,FF0000",
      'monit_state_37':"does not exist,FF0000",
      'monit_state_38':"permission failed,FF0000",
      'monit_state_39':"pid failed,FF0000",
      'monit_state_40':"ppid failed,FF0000",
      'monit_state_41':"resource limit matched,CCCC00",
      'monit_state_42':"size failed,FF0000",
      'monit_state_43':"timeout,FF0000",
      'monit_state_44':"timestamp failed,FF0000",
      'monit_state_45':"uid failed,FF0000",      
    })
    return inherit_env
  
  def populate_vals(self):
    to_init=['monit down',]
    status=self.getenv_prefix('monit_state_')
    if self.getenv('full'):
      to_init+=[k for k,v in status]
    counts=CacheCounter(self.getenv('cache'))
    for i in to_init:
      counts[i]=0
    return counts
  
  def print_config(self):
    vals=self.populate_vals()
    print "graph_title %s"%self.getenv('title')
    print "graph_args --base 1000"
    print "graph_vlabel number"
    print "graph_category %s"%self.getenv('group')
    print "graph_order %s" % " ".join(self.graph_order(vals))
    status={}
    try:
      status=dict(self.gets('monit_state_'))
    except:
      pass
    for l in vals:
      #get color if available
      c=status.get(l,None)
      id=l.strip().replace(' ','_')
      print "%s.label %s" % (id,l)
      print "%s.draw AREASTACK" % id
      if c is not None:
        print "%s.colour %s"  % (id,c)

  def graph_order(self,alls):
    post=self.getenv('lastest').split(',')    
    middle=[i for i in alls if i not in post]  
    return [i.strip().replace(' ','_') for i in  middle+post]
  
  def parse_monit_row(self,matcher,row):
    status=None
    try:
      groups=matcher.match(row).groups()
    except AttributeError:
      pass
    else:
      status=groups[2].lower().strip()
    return status
  
  def main(self,argv=None, **kw): 
    if self.check_config(argv):
      self.print_config()
    else:  
      matcher=re.compile(self.getenv('line_regex'))
      counts=self.populate_vals()
      if len(counts)==0:
        sys.stderr.write('Not configured: see documentation\n')
      else:
        csensors=1
        try:
          pid=int(subprocess.check_output(['pidof','monit'],stderr=subprocess.STDOUT).strip())
        except (subprocess.CalledProcessError, ValueError):
          #if fails means that the process is not running
          counts['monit down']=1
        else:
          csensors=0
          sensors=subprocess.check_output(['monit','summary'],stderr=subprocess.STDOUT)
          for row in sensors.split('\n'):
            status=self.parse_monit_row(matcher,row)
            if status is not None:
              counts[status]=counts[status]+1
              csensors+=1

        norm=lambda x:x
        if self.getenv('percentage'):
          norm=lambda x:(x*100/csensors)
          
        for l,v in counts.items():
          id=l.replace(' ','_')
          print "%s.value %s"% (id,norm(v))
            
        counts.store_in_cache()
  

def main(argv=None, **kw): 
  Monit().main()

if __name__ == '__main__':
  main()



