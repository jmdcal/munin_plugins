"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'

import os
import re

from munin_plugins.plugins.processes_analyzers.base import sensor
from munin_plugins.env import CACHE

class storages_snsr(sensor):
  sys_mtd='storages'
  proc_mtd='get_open_files'
  id_column='path'
  
  @property
  def _env(self):
    inherit_env=super(storages_snsr,self)._env
    inherit_env.update({
      'subtitle':'Disk Usage',
      'label':'bytes',      
      'cache':'%s/processesstorages'%CACHE,
      'files_regex':'.*((Data\.fs)|(\.log)).*',
      'graph':'AREASTACK',
    })
    return inherit_env
    
  def _evaluate(self,cache_id,curr):
    prev=self.getValue(cache_id,curr)
    res=[]
    parser=re.compile(self.getenv('files_regex'))
    if curr is not None and len(curr)>0:      
      res=set([(self._cut(i.path),os.path.getsize(i.path)) for i in curr if parser.match(i.path)])
    elif prev is not None:
      for i in prev:
        path=getattr(i,'path',i.get('path'))          
        if parser.match(path):
          size=0
          try:
            size=os.path.getsize(path)
          except OSError:
            #file not found (usually a pid file or lock)
            pass
          res.append((self._cut(path),size))
    return res 
  
  