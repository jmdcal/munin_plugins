"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'

import re

from munin_plugins.utils import CacheCounter

from munin_plugins.env import CACHE

from munin_plugins.plugins.www_analyzers.base import BaseCounter

class BotsCounter(BaseCounter):
  id='botscounter'
  
  @property
  def _env(self):
    inherit_env=super(BotsCounter,self)._env
    inherit_env.update({
      'subtitle':'Bots Requests',
      'label':"number",
      'cache':"%s/bots"%CACHE,
      'codes':'200',      
    })
    return inherit_env
    
  def __init__(self):
    super(BotsCounter,self).__init__()
    self.counter=CacheCounter(self.getenv('cache'),None)
    
  def update_with(self,datas):    
    codes=str(self.getenv('codes')).split(',')
    if str(datas.get_int_code()) in codes:
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
    dom=re.search('http://(.*?)(/|\))',agent).group(0)
  except AttributeError:
    dom=''
    
  if len(dom)>0:
    res=dom.replace('http:','').replace('/','')
  else:
    eml=re.findall("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}",agent)
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
   

