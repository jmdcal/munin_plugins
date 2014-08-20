"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'

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
  