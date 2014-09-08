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
import cgi
import sys

from collections import Counter

from munin_plugins.plugins.plugin import Plugin
from munin_plugins.utils import CacheCounter
from munin_plugins.env import CACHE

class Errfiles(Plugin):
  _prefix_name='snsr_errfiles'
  
  @property
  def _env(self):
    inherit_env=super(Errfiles,self)._env
    inherit_env.update({
      'title':'Error counter',
      'group':'file',
      'file_0':"/var/log/syslog",
      'filter_0':"(.*)(ERROR|error)(.*)",
      'warning_0':100,
      'critical_0':1000,
    })
    return inherit_env
  
  def get_files(self):
    files=self.getenv_prefix_with_id('file_')
    filters=dict(self.getenv_prefix_with_id('filter_'))
    w=dict(self.getenv_prefix_with_id('warning_'))
    c=dict(self.getenv_prefix_with_id('critical_'))    
    return [(ff,filters.get(id,'undef'),w.get(id,0),c.get(id,0)) for id,ff in files]    
  
  def _fn_to_id(self,fn):
    return fn.strip().replace(' ','_').replace('/','_')
  
  def print_config(self):
    print "graph_title %s"%self.getenv('title')
    print "graph_args --base 1000"
    print "graph_vlabel number"
    print "graph_category %s"%self.getenv('group')
    for ff,flt,w,c in self.get_files():
      id=self._fn_to_id(ff)
      print "%s.label %s" % (id,ff)
      print "%s.draw AREASTACK" % id
      print "%s.info %s"%(id,cgi.escape(flt))
      print "%s.warning %s"%(id,w)
      print "%s.critical %s"%(id,c)
  
  def main(self,argv=None, **kw): 
    if self.check_config(argv):
      self.print_config()
    else:        
      files=self.get_files()
      if len(files)==0:
        sys.stderr.write('Not configured: see documentation\n')
      else:
        for ff,flt,w,c in files:
          id=self._fn_to_id(ff)
          count=0
          matcher=re.compile(flt)
          try:                        
            with open(ff,'r') as fi:
              for row in fi:
                if matcher.match(row):
                  count+=1
          except IOError:
            sys.stderr.write('NotExists: file %s not exists!\n'%filename)
          print "%s.value %s"%(id,count)
      
      

  

def main(argv=None, **kw): 
  Errfiles().main()

if __name__ == '__main__':
  main()



