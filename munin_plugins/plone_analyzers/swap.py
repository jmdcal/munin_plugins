from munin_plugins.plone_analyzers.base import sensor

class swap_snsr(sensor):
  label='swap'
  cache=None
  sys_mtd='swap'
  proc_mtd='get_memory_maps'
  graph="AREASTACK"
  
  def _evaluate(self,ache_id,curr):
    return sum(i.swap for i in curr)

  