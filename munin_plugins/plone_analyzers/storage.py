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
    
    if curr is not None:
      res=[(self._cut(i.path),os.path.getsize(i.path)) for i in curr if re.match('.*((Data\.fs)|(\.log)).*',i.path)]
    elif prev is not None:
      for i in prev:
        size=0
        try:
          size=os.path.getsize(i.get('path'))
        except OSError:
          #file not found (usually a pid file or lock)
          pass
        res.append((self._cut(i.get('path')),size))
    else:            
      res=()
    return res 
  
  #def _filter(self,curr):
    #res=None
    #if curr is not None:
      #res=[(self._cut(i.path),os.path.getsize(i.path)) for i in curr if re.match('.*((Data\.fs)|(\.log)).*',i.path)]
    
    #return res