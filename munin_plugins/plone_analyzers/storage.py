import os
import re

from collections import deque

from munin_plugins.plone_analyzers.base import sensor

class storages_snsr(sensor):
  label='file'
  cache=None
  sys_mtd='storages'
  proc_mtd='get_open_files'
  graph="AREASTACK"
  
  def _evaluate(self,cache_id,curr):
    return [(self._cut(i.path),os.path.getsize(i.path)) for i in curr if not re.match('^(.*)\.lock$',i.path)]
  
  