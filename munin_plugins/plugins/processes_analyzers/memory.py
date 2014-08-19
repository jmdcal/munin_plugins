from munin_plugins.plugins.processes_analyzers.base import sensor
  
class memory_snsr(sensor):
  sys_mtd='memory_percent'
  proc_mtd='get_memory_percent'
  
  @property
  def _env(self):
    inherit_env=super(memory_snsr,self)._env
    inherit_env.update({
      'subtitle':'Memory Usage',
      'label':'%',
      'graph':"AREASTACK",
    })
    return inherit_env
  
  def _evaluate(self, cache_id,curr):
    if curr is None:
      curr=0    
    return curr
  