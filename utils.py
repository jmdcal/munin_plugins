#configuration file
from datetime import datetime,timedelta
import re
import time
import os
import fcntl
from base64 import b16decode

from collections import Counter
from collections import deque

from etc.env import NGINX_LOGS
from etc.env import MINUTES
from etc.env import VALID_CTYPES
from etc.env import ROW_PARSER
from etc.env import ROW_MAPPING
from etc.env import NGINX_PARSER
from etc.env import EMAIL_PARSER
from etc.env import DOM_PARSER
from etc.env import WRONG_AGENTS

def getlimit(minutes=MINUTES):
  actual_time=datetime.today()
  delay=timedelta(seconds=minutes*60)
  return actual_time-delay

class RowParser(object):
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

  def get_bytes(self):
    return self._get_val('bytes')
    
  def get_reffer(self):
    return self._get_val('reffer')

  def get_agent(self):
    return self._get_val('agent')

  def get_latency(self):
    return self._get_val('latency')

  def is_valid_line(self,https=[]):
    try:
      code=int(self.get_code())
    except ValueError:
      code=self.get_code()
    except TypeError:      
      #no valid code is parsed
      code=0
    return (len(https)==0 or code in https)

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
    else:
      fd=open(WRONG_AGENTS,'a')
      fd.write('%s\n'%agent)
      fd.close()
  
  try:
    res=res.split(' ')[0]
  except:
    pass
  # fix for Googlebot-Image/1.0 and others with no useful agent signature
  if len(res)==0:
    res=agent.lower().replace('/','_')    
    

  return res.replace('.','_').replace('@','_at_')
       
def ft(time_ft):
  # this function is needed in apache because latency is not in seconds
  # return time in seconds.millisec
  return float(time_ft)

def change_format(dt):
  day,month,dd,tm,year=dt.split(' ')
  date=time.strptime('%s/%s/%s'%(dd,month,year),'%d/%b/%Y')
  return "%s %s.000000"%(time.strftime('%Y-%m-%d',date),tm)

def getparams(this):
  script_name=this.split('/')[-1]
  full_path=os.path.realpath(this)
  real_name=full_path.split('/')[-1][:-3]
  parts=script_name.replace(real_name+'_','').split('_')
  title=b16decode(parts[0])
  group=parts[1]
  filename=b16decode(parts[2])
  return full_path.replace('runner','worker'),title,group,'%s/%s'%(NGINX_LOGS,filename)

#Mixin Cache Class
class Cache(object): 
  default=None
  
  def __init__(self,fn,def_value=None,*args,**kargs):
    super(Cache,self).__init__(*args,**kargs)
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
    if os.path.isfile(self.fn):
      fd=open(self.fn,'r')
      for i in fd:
        i=i.strip()
        if len(i)>0:
          self.load_value(i)
      fd.close()

  def store_in_cache(self):   
    exists=os.path.isfile(self.fn)
    mode='w'
    if exists:
      mode='r+'
      
    fd=open(self.fn,mode)    
    self._lock(fd)
    
    values=self.get_values()
    if exists:
      for i in fd:
        try:
          values.remove(i.strip())
        except ValueError:
          #We try to remove from values what is yet in cache file
          pass
      
    #now in values we have only new values for cache and we will append to file
    for l in values:
      fd.write('%s\n'%l)
      
    self._unlock(fd)
    fd.close()

  #Methods to define in class
  def load_value(self,val):
    pass

  def get_values(self):
    return []

#Simple cache based on a list of values
class CacheDict(Cache,dict):  
  def load_value(self,val):
    self[val]=self.default

  def get_values(self):
    return self.keys()

#Simple cache based on a Counter, a dictionary val: qty
class CacheCounter(Cache,Counter):    
  default=0
  
  def load_value(self,val):
    self[val]=self.default

  def get_values(self):
    return self.keys()
