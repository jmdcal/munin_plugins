from .base import sensor
from ..env import CACHE
from ..utils import get_percent_of

class cpu_usage_snsr(sensor):
  label='cpu usage (%)'
  cache='%s/javaprocess'%CACHE
  sys_mtd='cpu_times'
  proc_mtd='get_cpu_times'
  graph="AREASTACK"
  
  def _evaluate(self,cache_id,curr):    
    prev=self.getValue(cache_id,curr)    
    pdff=self._mkdiff(prev,curr)          
    return get_percent_of(pdff,self._sysdiff()) 
    