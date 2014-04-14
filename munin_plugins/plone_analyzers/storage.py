import os
import re

from collections import deque
from munin_plugins.etc.env import CACHE
from munin_plugins.plone_analyzers.base import sensor

class storages_snsr(sensor):
  label='file'
  cache='%s/zopestorages'%CACHE
  sys_mtd='storages'
  proc_mtd='get_open_files'
  graph="AREASTACK"
  id_column='path'
  
  def _evaluate(self,cache_id,curr):
    prev=self.getValue(cache_id,curr)
    res=[]
    if curr is not None and len(curr)>0:      
      res=set([(self._cut(i.path),os.path.getsize(i.path)) for i in curr if re.match('.*((Data\.fs)|(\.log)).*',i.path)])
    elif prev is not None:
      for i in prev:
        path=getattr(i,'path',i.get('path'))          
        if re.match('.*((Data\.fs)|(\.log)).*',path):
          size=0
          try:
            size=os.path.getsize(path)
          except OSError:
            #file not found (usually a pid file or lock)
            pass
          res.append((self._cut(path),size))
    else:            
      res=()
    return res 
    