from collections import Counter

from munin_plugins.etc.env import HTTP_CODES
from munin_plugins.etc.env import MINUTES
from base import BaseCounter

class HttpCodesCounter(BaseCounter):
  id='httpcodescounter'
  base_title="Nginx http codes"
  
  def __init__(self,title,group):
    super(HttpCodesCounter,self).__init__(title,group)
    self.label="q.ty in %s mins"%MINUTES
    self.counter=Counter(dict([(str(i),0) for i in HTTP_CODES.keys()]))
    
  def update_with(self,datas):
    if datas.get_int_code() in HTTP_CODES.keys():
      code=datas.get_code()
      self.counter[code]=self.counter[code]+1
              
  def print_data(self, printer, w=None, c=None):
    for k,l in sorted(HTTP_CODES.items()):      
      printer(id="code%s"%k,
              value=self.counter[str(k)],
              label="[%s] %s "%(k,l),)
