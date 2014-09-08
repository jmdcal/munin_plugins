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
from datetime import datetime

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
      'minutes':5,
      'file_0':"/var/log/syslog",
      'filter_0':"(.*)(ERROR|error)(.*)",
      'date_filter_0':'^(\w{3}\s(\s|\d)\d\s+\d{2}:\d{2}:\d{2})',
      'date_converter_0':"%b %d %H:%M:%S",
      'warning_0':100,
      'critical_0':1000,
    })
    return inherit_env
  
  def get_files(self):
    files=self.getenv_prefix_with_id('file_')
    filters=dict(self.getenv_prefix_with_id('filter_'))
    df=dict(self.getenv_prefix_with_id('date_filter_'))
    dc=dict(self.getenv_prefix_with_id('date_converter_'))    
    w=dict(self.getenv_prefix_with_id('warning_'))
    c=dict(self.getenv_prefix_with_id('critical_'))    
    return [(ff,filters.get(id,'undef'),df.get(id,None),dc.get(id,None),w.get(id,0),c.get(id,0)) for id,ff in files]    
  
  def _fn_to_id(self,fn):
    return fn.strip().replace(' ','_').replace('/','_')
  
  def _fix_year(self,dt):
    ty=datetime.now().year    
    if dt.year!=ty and dt.year!=ty-1:
      dt=dt.replace(ty)      
    return dt  
  
  def print_config(self):
    print "graph_title %s"%self.getenv('title')
    print "graph_args --base 1000"
    print "graph_vlabel number"
    print "graph_category %s"%self.getenv('group')
    for ff,flt,df,dc,w,c in self.get_files():
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
        limit=self.getlimit(self.getenv('minutes'))
        for ff,flt,df,dc,w,c in self.get_files():
          id=self._fn_to_id(ff)
          count=0
          matcher=re.compile(flt)
          dmatcher=re.compile(df)
          try:                        
            with open(ff,'r') as fi:
              for row in fi:
                ds=dmatcher.search(row).group()
                dt=self._fix_year(datetime.strptime(ds,dc))                                
                if dt>limit and matcher.match(row):
                  count+=1
          except IOError:
            sys.stderr.write('NotExists: file %s not exists!\n'%filename)
          print "%s.value %s"%(id,count)
      
def main(argv=None, **kw): 
  Errfiles().main()

if __name__ == '__main__':
  main()



