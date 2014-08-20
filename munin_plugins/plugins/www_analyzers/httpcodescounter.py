"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'

from munin_plugins.utils import CacheCounter

from munin_plugins.env import CACHE
from munin_plugins.plugins.www_analyzers.base import BaseCounter

class HttpCodesCounter(BaseCounter):
  id='httpcodescounter'
  
  @property
  def _env(self):
    inherit_env=super(HttpCodesCounter,self)._env
    inherit_env.update({
      'subtitle':'Response Codes',
      'label':"number",
      'cache':"%s/httpcodes"%CACHE,
      'title_100':"Continue",
      'title_101':"Switching Protocols",
      'title_200':"OK",
      'title_201':"Created",
      'title_202':"Accepted",
      'title_203':"Non-Authoritative Information",
      'title_204':"No Content",
      'title_205':"Reset Content",
      'title_206':"Partial Content",
      'title_300':"Multiple Choices",
      'title_301':"Moved Permanently",
      'title_302':"Found",
      'title_303':"See Other",
      'title_304':"Not Modified",
      'title_305':"Use Proxy",
      'title_306':"(Unused)",
      'title_307':"Temporary Redirect",
      'title_400':"Bad Request",
      'title_401':"Unauthorized",
      'title_402':"Payment Required",
      'title_403':"Forbidden",
      'title_404':"Not Found",
      'title_405':"Method Not Allowed",
      'title_406':"Not Acceptable",
      'title_407':"Proxy Authentication Required",
      'title_408':"Request Timeout",
      'title_409':"Conflict",
      'title_410':"Gone",
      'title_411':"Length Required",
      'title_412':"Precondition Failed",
      'title_413':"Request Entity Too Large",
      'title_414':"Request-URI Too Long",
      'title_415':"Unsupported Media Type",
      'title_416':"Requested Range Not Satisfiable",
      'title_417':"Expectation Failed",
      'title_444':"No Response for malware",
      'title_499':"Client closed the connection",
      'title_500':"Internal Server Error",
      'title_501':"Not Implemented",
      'title_502':"Bad Gateway",
      'title_503':"Service Unavailable",
      'title_504':"Gateway Timeout",
      'title_505':"HTTP Version Not Supported",      
    })
    return inherit_env  
  
  def __init__(self):
    super(HttpCodesCounter,self).__init__()
    self.counter=CacheCounter(self.getenv('cache'),None)
    
  def update_with(self,datas):
    code=datas.get_code()
    self.counter[code]=self.counter[code]+1
              
  def print_data(self, printer, w=None, c=None):
    if len(self.counter.items())>0:
      for k,v in self.counter.items():
        printer(id="code%s"%k,
          value=v,
          label="[%s] %s"%(k,self.getenv('title_%s'%k)))
    else:    
      printer(id='none',
              value=0,
              label='[] no request',
      )
  
  def update_cache(self):
    self.counter.store_in_cache()