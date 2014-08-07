#configuration file
from datetime import datetime,timedelta
import re
import time
import fcntl
import pickle
from base64 import b64encode
from base64 import b64decode

from collections import Counter
from collections import deque

from os.path import isfile

from munin_plugins.env import MINUTES

EMAIL_PARSER=re.compile("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}")
DOM_PARSER=re.compile('http://(.*?)(/|\))')

#Forced Option, may be one day I move these in mmunin_plugins.conf

#Nginx log Format
#    log_format combined2 '$remote_addr - $remote_user [$time_local]  '
#                    '"$request" $status $body_bytes_sent '
#                    '"$http_referer" "$http_user_agent" [[$request_time]]';
#
# This is an example about the nginx log row
# 192.107.92.74 - - [25/Jun/2013:03:51:59 +0200]  "GET /++theme++enea-skinaccessibile/static/theme/styles/polaroid-multi.png HTTP/1.1" 499 0 "-" "Serf/1.1.0 mod_pagespeed/1.5.27.3-3005" [[2.554]]
NGING_IP_RE=r'^([0-9]+(?:\.[0-9]+){3})'
NGINX_USER_RE=r'\s+\-\s(.*?)'
NGINX_DATE_RE=r'\s+\[([0-9]{2}\/[a-zA-Z]{3}\/[0-9\:]{13})\s\+[0-9]{4}\]'
NGINX_REQUEST_RE=r'\s+\"([A-Z]*?)\s(.*?)(\sHTTP.*)?"'
NGINX_HTTPCODE_RE=r'\s+([0-9]{3})'
NGINX_BYTES_RE=r'\s+([\-0-9]+)'
NGINX_REFFER_RE=r'\s+\"(.*?)\"'
NGINX_SIGN_RE=r'\s+\"(.*?)\"'
NGINX_LATENCY_RE=r'\s+\[\[(.*)\]\]'

NGINX_LOG_RE= \
  NGING_IP_RE + \
  NGINX_USER_RE + \
  NGINX_DATE_RE + \
  NGINX_REQUEST_RE + \
  NGINX_HTTPCODE_RE + \
  NGINX_BYTES_RE + \
  NGINX_REFFER_RE + \
  NGINX_SIGN_RE

NGINX_PARSER=re.compile(NGINX_LOG_RE)
ROW_PARSER=re.compile(NGINX_LOG_RE+NGINX_LATENCY_RE)

APACHE_PARSER=re.compile(NGINX_LOG_RE)
AROW_PARSER=re.compile(NGINX_LOG_RE+NGINX_LATENCY_RE)

ROW_MAPPING={
  'ip':0,
  'user':1,
  'date':2,
  'method':3,
  'url':4,
  'protocol':5,
  'code':6,
  'bytes':7,
  'reffer':8,
  'agent':9,
  'latency':10,
}

class NginxRowParser(object):
  def __init__(self,row):
    self.row=row
    try:
      self.parsed=ROW_PARSER.search(row).groups()
    except AttributeError:
      #Fall back to combine nginx log
      try:
        self.parsed=NGINX_PARSER.search(row).groups()
      except AttributeError:        
        self.parsed=[]

  def _get_val(self,lab):
    try:
      res=self.parsed[ROW_MAPPING[lab]]
    except IndexError:
      res=None
    return res

  def get_ip(self):
    return self._get_val('ip')

  def get_user(self):
    return self._get_val('user')

  def get_date(self):
    dd=self._get_val('date')
    try:
      dt=datetime.strptime(dd,'%d/%b/%Y:%H:%M:%S')
    except:
      dt=dd
    return dt

  def get_method(self):
    return self._get_val('method')
    
  def get_url(self):
    return self._get_val('url')

  def get_protocol(self):
    return self._get_val('protocol')

  def get_code(self):
    return self._get_val('code')

  def get_int_code(self):
    try:
      code=int(self.get_code())
    except ValueError:
      code=-1
    except TypeError:      
      #no valid code is parsed
      code=-1      
    return code

  def get_bytes(self):
    res=None
    if self._get_val('bytes') is not None:
      try:
        res=int(self._get_val('bytes'))
      except (ValueError,TypeError):      
        pass      
    return res
    
  def get_reffer(self):
    return self._get_val('reffer')

  def get_agent(self):
    return self._get_val('agent')

  def get_latency(self):
    return self._get_val('latency')
  
  def get_float_latency(self):
    res=None
    if self.get_latency() is not None:
      res=float(self.get_latency())
    return res
  
  def is_valid_line(self,https=[]):
    try:
      code=int(self.get_code())
    except ValueError:
      code=self.get_code()
    except TypeError:      
      #no valid code is parsed
      code=0
    return (len(https)==0 or code in https)

class ApacheRowParser(NginxRowParser):
  def __init__(self,row):
    self.row=row
    try:
      self.parsed=AROW_PARSER.search(row).groups()
    except AttributeError:
      #Fall back to combine nginx log
      try:
        self.parsed=APACHE_PARSER.search(row).groups()
      except AttributeError:        
        self.parsed=[]
  
  def get_float_latency(self):
    res=super(ApacheRowParser,self).get_float_latency()
    if res is not None:
      res=res/1000000
    return res
    
def mkoutput(**argv):
  id=argv.get('id',None)
  if id is not None:
    del argv['id']
    for k,v in argv.items():
      if v is not None:
        try:
          print "%s.%s %.3f"%(id,k,v)
        except TypeError:
          print "%s.%s %s"%(id,k,v)

def print_data(**args):
  id=args.get('id',None)
  v=args.get('value',None)
  if id is not None and v is not None:
    mkoutput(id=id,
             value=v)

def print_config(**args):
  id=args.get('id',None)
  l=args.get('label',None)
  if id is not None and l is not None:
    mkoutput(id=id,
             label=l,
             draw=args.get('draw',None),
             type=args.get('type',None),
             warning=args.get('warning',None),
             critical=args.get('critical',None),
             colour=args.get('color',None),
             line=args.get('line',None),)
        
#Mixin Cache Class
class _Cache(object): 
  default=None
  
  def __init__(self,fn,def_value=None,*args,**kargs):
    super(_Cache,self).__init__(*args,**kargs)
    self.fn=fn       
    if def_value is not None:
      self.default=def_value
    self.load_from_cache()
    
  def _lock(self,fd):
    locked=False
    while not locked:
      try:
        fcntl.lockf(fd,fcntl.LOCK_EX)
      except IOError:
        time.sleep(3)
      else:
        locked=True
    
  def _unlock(self,fd):  
    fcntl.lockf(fd, fcntl.LOCK_UN)

  def load_from_cache(self):
    if self.fn is not None and isfile(self.fn):
      fd=open(self.fn,'r')
      for i in fd:
        i=i.strip()
        if len(i)>0:
          self.load_value(i)
      fd.close()

  def store_in_cache(self):   
    if self.fn is not None:
      fd=open(self.fn,'w')    
      self._lock(fd)
                   
      #now in values we have only new values for cache and we will append to file
      for l in self.get_values():
        fd.write('%s\n'%l)
        
      self._unlock(fd)
      fd.close()

  #Methods to define in class
  def load_value(self,val):
    pass

  def get_values(self):
    return []

#Simple cache based on a list of values
class CacheDict(_Cache,dict):  
  def load_value(self,val):
    self[val]=self.default

  def get_values(self):
    return self.keys()

#Simple cache based on a Counter, a dictionary val: qty
class CacheCounter(_Cache,Counter):    
  default=0
  
  def load_value(self,val):
    self[val]=self.default

  def get_values(self):
    return self.keys()

class CachePickle(_Cache,dict):
  default=()
  
  def load_value(self,val):
    try:
      id,pickled=val.split(' ')
      self[id]=pickle.loads(b64decode(pickled))  
    except:
      self[val]=self.default

  def get_values(self):
    res=deque()
    for k,data in self.items():
      pickled=b64encode(pickle.dumps(data))
      res.append("%s %s"%(k,pickled))
    return res
    
    
    
