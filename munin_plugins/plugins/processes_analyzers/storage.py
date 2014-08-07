import os
import re

from munin_plugins.plugins.processes_analyzers.base import sensor
from munin_plugins.env import CACHE

class storages_snsr(sensor):
  label='file'
  sys_mtd='storages'
  proc_mtd='get_open_files'
  id_column='path'
  _defaults={
    'cache':'%s/processesstorages'%CACHE,
    'files_regex':'.*((Data\.fs)|(\.log)).*',
    'graph':'AREASTACK',
  }
  
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
  
  