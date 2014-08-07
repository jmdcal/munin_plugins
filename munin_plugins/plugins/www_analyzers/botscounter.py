from munin_plugins.utils import *

from munin_plugins.env import CACHE

from munin_plugins.plugins.www_analyzers.base import BaseCounter

CACHE_BOTS="%s/bots"%CACHE

class BotsCounter(BaseCounter):
  id='botscounter'
  base_title="Bots"
  
  def __init__(self,title,group):
    super(BotsCounter,self).__init__(title,group)
    self.label="number of calls"
    self.counter=CacheCounter(CACHE_BOTS)
    
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


def get_short_agent(agent):
  res=''
  try:
    dom=DOM_PARSER.search(agent).group(0)
  except AttributeError:
    dom=''
    
  if len(dom)>0:
    res=dom.replace('http:','').replace('/','')
  else:
    eml=EMAIL_PARSER.findall(agent)
    if len(eml)>0:
      res=eml[0]  
  try:
    res=res.split(' ')[0]
  except:
    pass
  # fix for Googlebot-Image/1.0 and others with no useful agent signature
  if len(res)==0:
    res=agent.lower().replace('/','_')    
    

  return res.replace('.','_').replace('@','_at_').replace('(',' ').replace(')',' ')
   

