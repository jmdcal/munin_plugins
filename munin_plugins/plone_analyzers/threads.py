from munin_plugins.plone_analyzers.base import sensor

from collections import deque
from munin_plugins.etc.env import CACHE

from munin_plugins.utils import namedtuple2dict
  
class threads_snsr(sensor):
  label='threads #'
  cache='%s/zopethreads'%CACHE
  sys_mtd='cpu_times'
  proc_mtd='get_threads'
  graph="AREASTACK"
  id_column="id"

  def _evaluate(self,cache_id,curr):              
    res=0
    if curr is not None:
      res=len(curr)
      
    return res

  
  