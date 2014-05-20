from ..utils import CacheCounter
from ..env import HTTP_CODES
from ..env import CACHE_APACHE_HTTP_CODES
from ..env import MINUTES
from .base import BaseCounter

class HttpCodesCounter(BaseCounter):
  id='httpcodescounter'
  base_title="Apache http codes"
  
  def __init__(self,title,group):
    super(HttpCodesCounter,self).__init__(title,group)
    self.label="q.ty in %s mins"%MINUTES
    self.counter=CacheCounter(CACHE_APACHE_HTTP_CODES)
    
  def update_with(self,datas):
    code=datas.get_code()
    self.counter[code]=self.counter[code]+1
              
  def print_data(self, printer, w=None, c=None):
    if len(self.counter.items())>0:
      for k,v in self.counter.items():
        printer(id="code%s"%k,
                value=v,
                label="[%s] %s "%(k,HTTP_CODES.get(int(k),'undefined')),)
    else:    
      printer(id='none',
              value=0,
              label='[] no request',
              )
  
  def update_cache(self):
    self.counter.store_in_cache()