from .base import sensor
from ..env import CACHE
  
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

  
  