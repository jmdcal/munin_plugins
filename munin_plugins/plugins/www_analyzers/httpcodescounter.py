from munin_plugins.utils import CacheCounter

from munin_plugins.env import CACHE
from munin_plugins.plugins.www_analyzers.base import BaseCounter

CODES={
  100:"Continue",
  101:"Switching Protocols",
  200:"OK",
  201:"Created",
  202:"Accepted",
  203:"Non-Authoritative Information",
  204:"No Content",
  205:"Reset Content",
  206:"Partial Content",
  300:"Multiple Choices",
  301:"Moved Permanently",
  302:"Found",
  303:"See Other",
  304:"Not Modified",
  305:"Use Proxy",
  306:"(Unused)",
  307:"Temporary Redirect",
  400:"Bad Request",
  401:"Unauthorized",
  402:"Payment Required",
  403:"Forbidden",
  404:"Not Found",
  405:"Method Not Allowed",
  406:"Not Acceptable",
  407:"Proxy Authentication Required",
  408:"Request Timeout",
  409:"Conflict",
  410:"Gone",
  411:"Length Required",
  412:"Precondition Failed",
  413:"Request Entity Too Large",
  414:"Request-URI Too Long",
  415:"Unsupported Media Type",
  416:"Requested Range Not Satisfiable",
  417:"Expectation Failed",
  444:"No Response for malware",
  499:"Client closed the connection",
  500:"Internal Server Error",
  501:"Not Implemented",
  502:"Bad Gateway",
  503:"Service Unavailable",
  504:"Gateway Timeout",
  505:"HTTP Version Not Supported",
}

CACHE_CODES="%s/httpcodes"%CACHE

class HttpCodesCounter(BaseCounter):
  id='httpcodescounter'
  base_title="Http codes"
  
  def __init__(self,title,group):
    super(HttpCodesCounter,self).__init__(title,group)
    self.label="q.ty "
    self.counter=CacheCounter(CACHE_CODES)
    
  def update_with(self,datas):
    code=datas.get_code()
    self.counter[code]=self.counter[code]+1
              
  def print_data(self, printer, w=None, c=None):
    if len(self.counter.items())>0:
      for k,v in self.counter.items():
        printer(id="code%s"%k,
                value=v,
                label="[%s] %s "%(k,CODES.get(int(k),'undefined')),)
    else:    
      printer(id='none',
              value=0,
              label='[] no request',
              )
  
  def update_cache(self):
    self.counter.store_in_cache()