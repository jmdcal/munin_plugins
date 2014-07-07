#configuration file
from datetime import datetime,timedelta
import re
import time
import os
import fcntl
import pickle
import sys
from base64 import b16encode
from base64 import b16decode
from base64 import b64encode
from base64 import b64decode

from collections import Counter
from collections import deque

from os.path import join
from os.path import exists

from .env import MINUTES
from .env import ROW_PARSER
from .env import ROW_MAPPING
from .env import NGINX_PARSER
from .env import EMAIL_PARSER
from .env import DOM_PARSER
from .env import WRONG_AGENTS

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
    return self._get_val('bytes')
    
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
    

  return res.replace('.','_').replace('@','_at_').replace('(',' ').replace(')',' ')
       
def ft(time_ft):
  # this function is needed in apache because latency is not in seconds
  # return time in seconds.millisec
  return float(time_ft)

def change_format(dt):
  day,month,dd,tm,year=dt.split(' ')
  date=time.strptime('%s/%s/%s'%(dd,month,year),'%d/%b/%Y')
  return "%s %s.000000"%(time.strftime('%Y-%m-%d',date),tm)

def getparams_from_config():
  files=deque()
  end=False
  file_no=0
  filename=''
  while filename is not None:
    title=os.environ.get('GRAPH_TITLE_%s'%file_no,'Untitled')
    group=os.environ.get('GRAPH_GROUP_%s'%file_no,'Undefined')
    filename=os.environ.get('GRAPH_ACCESS_%s'%file_no,None)  
    if filename is not None:
      files.append((title,group,filename))
      file_no+=1
        
  return files

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
    
def concat(tp):
  return '%s::%s'%tp

def namedtuple2list(nt,conv=lambda x: x):
  try:
    res=[conv((i,getattr(nt,i))) for i in nt._fields]
  except AttributeError:
    res=[]
  return res

def namedtuple2dict(nt,conv=lambda x: x):
  return dict(namedtuple2list(nt,conv))

def get_percent_of(val,full):
  try:
    percent = (val / full) * 100
  except ZeroDivisionError:
    # interval was too low
    percent = 0.0
  return percent
    


def check_install(argv):
  argv=fixargs(argv)
  return (len(argv)>0 and argv[0]=='install')
    
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
    if self.fn is not None and os.path.isfile(self.fn):
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

class CachePickle(Cache,dict):
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
    
    
    
