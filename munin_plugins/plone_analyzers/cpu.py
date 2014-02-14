from munin_plugins.plone_analyzers.base import sensor

from munin_plugins.utils import CACHE
from munin_plugins.utils import get_percent_of
from munin_plugins.utils import namedtuple2dict

class cpu_usage_snsr(sensor):
  label='cpu usage (%)'
  cache='%s/zopeprocess'%CACHE
  sys_mtd='cpu_times'
  proc_mtd='get_cpu_times'
  graph="AREASTACK"
  
  def _evaluate(cache_id,curr):    
    prev=self.pcache.get(cache_id,curr)    
    pdff=self.mkdiff(prev,curr)          
    return get_percent_of(pdff,self._sysdiff()) 
    