from munin_plugins.plone_analyzers.base import sensor

from collections import deque
from munin_plugins.etc.env import CACHE

from munin_plugins.utils import namedtuple2dict
  
class threads_snsr(sensor):
  label='threads usage (%)'
  cache='%s/zopethreads'%CACHE
  sys_mtd='cpu_times'
  proc_mtd='get_threads'
  graph="AREASTACK"

  def _evaluate(self,cache_id,curr):    
    sys_dff=self._sysdiff()
    curr_ids=[i.id for i in curr]
    prev=self.getValue(cache_id,[namedtuple2dict(i) for i in curr])    
    
    prev_dct=dict([(p['id'],p['system_time']+p['user_time']) for p in prev])
    res=deque()
    
    for c in curr:
      cv=c.user_time+c.system_time
      pv=prev_dct.get(c.id,cv)
      dff=self._mkdiff(pv,cv)
      if sys_dff==0:
        res.append((c.id,0))
      else:
        res.append((c.id,dff*100/sys_dff))
        
    for k,v in prev_dct.items():
      if k not in curr_ids:
        res.append((k,0))
          
    return res

  
  