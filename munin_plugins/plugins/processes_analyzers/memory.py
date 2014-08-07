from munin_plugins.plugins.processes_analyzers.base import sensor
  
class memory_snsr(sensor):
  label='memory (%)'
  sys_mtd='memory_percent'
  proc_mtd='get_memory_percent'
  _defaults={
    'graph':"AREASTACK"
  }
  
  def _evaluate(self, cache_id,curr):
    if curr is None:
      curr=0    
    return curr
  