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
   
class connections_snsr(sensor):
  sys_mtd='connections'
  proc_mtd='get_connections'
  
  @property
  def _env(self):
    inherit_env=super(connections_snsr,self)._env
    inherit_env.update({
      'subtitle':'Network Connections',
      'label':'number',
    })
    return inherit_env  
  
  def _evaluate(self,cache_id,curr):
    res=0
    try:
      res=len(curr)
    except:
      pass
    return res 

  