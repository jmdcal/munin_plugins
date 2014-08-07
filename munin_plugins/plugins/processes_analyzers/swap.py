from munin_plugins.plugins.processes_analyzers.base import sensor

class swap_snsr(sensor):
  label='swap'
  sys_mtd='swap'
  proc_mtd='get_memory_maps'
  _defaults={
    'graph':"AREASTACK",
  }
  
  def _evaluate(self,ache_id,curr):
    res=0
    try:
      res=sum(i.swap for i in curr)
    except TypeError:
      pass
    return res 

  