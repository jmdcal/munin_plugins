#configuration file
from datetime import datetime,timedelta
import re
import time
import os
from base64 import b16decode

from etc.env import LOGS
from etc.env import MINUTES
from etc.env import VALID_CTYPES
from etc.env import ROW_PARSER
from etc.env import ROW_MAPPING
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
    return (len(https)==0 or code in https)

def get_short_agent(agent):
  res=''
  try:
    dom=DOM_PARSER.search(agent).group(0)
  except AttributeError:
    fd=open(WRONG_AGENTS,'a')
    fd.write(agent)
    fd.close()
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
  return full_path.replace('runner','worker'),title,group,'%s/%s'%(LOGS,filename)

