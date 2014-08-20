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
from munin_plugins.env import CACHE
  
class io_counters_snsr(sensor):  
  sys_mtd='iocounters'
  proc_mtd='get_io_counters'
  
  @property
  def _env(self):
    inherit_env=super(io_counters_snsr,self)._env
    inherit_env.update({
      'subtitle':'I/O bytes',
      'label':'bytes',
      'cache':'%s/processesiosbytes'%CACHE,      
    })
    return inherit_env
  
  def _evaluate(self,cache_id,curr):
    prev=self.getValue(cache_id,{}) 
    res=()
    if curr is not None:
      res=[(k,self._mkdiff(prev.get(k,0),v)) for k,v in self.namedtuple2dict(curr).items() if '_bytes' in k]
    elif prev is not None:
      res=[(i,0) for i in prev.keys() if '_bytes' in i]
      
    return res

class io_counters_abs_snsr(sensor):
  sys_mtd='iocounters'
  proc_mtd='get_io_counters'
  
  @property
  def _env(self):
    inherit_env=super(io_counters_abs_snsr,self)._env
    inherit_env.update({
      'subtitle':'I/O request',
      'label':'number',      
      'cache':'%s/processesiosbytes'%CACHE
    })
    return inherit_env
  
  def _evaluate(self,cache_id,curr):
    prev=self.getValue(cache_id,{}) 
    res=()
    if curr is not None:
      res=[(k,self._mkdiff(prev.get(k,0),v)) for k,v in self.namedtuple2dict(curr).items() if '_count' in k]
    elif prev is not None:
      res=[(i,0) for i in prev.keys() if '_count' in i]
      
    return res

  
  