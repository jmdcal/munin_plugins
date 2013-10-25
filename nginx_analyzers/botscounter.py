from utils import *

from etc.env import CACHE_BOTS
from etc.env import MINUTES

from base import BaseCounter


class BotsCounter(BaseCounter):
  id='botscounter'
  
  def __init__(self,title,group):
    super(BotsCounter,self).__init__("Nginx Bots: %s"%title,group)
    self.label="number of call"
    self.counter=CacheCounter(CACHE_BOTS)
    
  def update_with(self,datas):    
    if datas.get_int_code() in [200,]:
      agent=datas.get_agent()
      agent=get_short_agent(agent)
      self.counter[agent]=1+self.counter[agent]
      
  def print_data(self, printer):
    for l,v in self.counter.items():
      printer(id=l,
              value=v,
              label="Number of pages asked by %s in %s mins"%(l,MINUTES),
              warning=10,
              critical=30,
              )

  def update_cache(self):
    self.counter.store_in_cache()