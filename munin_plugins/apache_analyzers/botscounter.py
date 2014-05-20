from ..utils import *

from ..env import CACHE_APACHE_BOTS
from ..env import MINUTES

from .base import BaseCounter

class BotsCounter(BaseCounter):
  id='botscounter'
  base_title="Apache Bots"
  
  def __init__(self,title,group):
    super(BotsCounter,self).__init__(title,group)
    self.label="number of call in %s mins"%MINUTES
    self.counter=CacheCounter(CACHE_APACHE_BOTS)
    
  def update_with(self,datas):    
    if datas.get_int_code() in [200,]:
      agent=datas.get_agent()
      if 'bot' in agent:
        agent=get_short_agent(agent)
        self.counter[agent]=1+self.counter[agent]
      
  def print_data(self, printer, w=10,c=30):
    if len(self.counter.items())>0:
      for l,v in self.counter.items():
        printer(id=l,
                value=v,
                label=l,
                warning=w,
                critical=c,
                )
    else:
      printer(id='none',
              value=0,
              label='none',
              warning=w,
              critical=c,
              )
      

  def update_cache(self):
    self.counter.store_in_cache()
