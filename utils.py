#configuration file
from datetime import datetime,timedelta
import re
import time
from etc.env import logs
from etc.env import MINUTES
from etc.env import VALID_CTYPES


#Nginx log Format

#    log_format combined2 '$remote_addr - $remote_user [$time_local]  '
#                    '"$request" $status $body_bytes_sent '
#                    '"$http_referer" "$http_user_agent" [[$request_time]]';
#192.107.92.74 - - [25/Jun/2013:03:51:59 +0200]  "GET /++theme++enea-skinaccessibile/static/theme/styles/treeExpanded.png HTTP/1.1" 499 0 "-" "Serf/1.1.0 mod_pagespeed/1.5.27.3-3005" [[2.553]]
#192.107.92.74 - - [25/Jun/2013:03:51:59 +0200]  "GET /++theme++enea-skinaccessibile/static/theme/styles/treeCollapsed.png HTTP/1.1" 499 0 "-" "Serf/1.1.0 mod_pagespeed/1.5.27.3-3005" [[2.553]]
#192.107.92.74 - - [25/Jun/2013:03:51:59 +0200]  "GET /++theme++enea-skinaccessibile/static/theme/styles/polaroid-single.png HTTP/1.1" 499 0 "-" "Serf/1.1.0 mod_pagespeed/1.5.27.3-3005" [[2.554]]
#192.107.92.74 - - [25/Jun/2013:03:51:59 +0200]  "GET /++theme++enea-skinaccessibile/static/theme/styles/polaroid-multi.png HTTP/1.1" 499 0 "-" "Serf/1.1.0 mod_pagespeed/1.5.27.3-3005" [[2.554]]


#this pattern produce:
# ('192.107.92.74',
#  '-',
#  '25/Jun/2013:03:51:59',
#  'GET',
#  '/++theme++enea-skinaccessibile/static/theme/styles/polaroid-multi.png',
#  ' HTTP/1.1', 
#  '499',
#  '0',
#  '-',
#  'Serf/1.1.0 mod_pagespeed/1.5.27.3-3005',
#  '2.554')

row_pattern=(
  r'^([0-9]+(?:\.[0-9]+){3})' #IP
  r'\s+\-\s(.*?)' #user
  r'\s+\[([0-9]{2}\/[a-zA-Z]{3}\/[0-9\:]{13})\s\+[0-9]{4}\]' #date
  r'\s+\"([A-Z]*?)\s(/.*?)(\sHTTP.*)?"' #request
  r'\s+([0-9]{3})' #http code
  r'\s+([0-9]+)' #bytes code
  r'\s+\"(.*?)\"' #reffer
  r'\s+\"(.*?)\"' #signature
  r'\s+\[\[(.*)\]\]' #latency
)

parser=re.compile(row_pattern)
email_pattern=re.compile("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}")
dom_pattern=re.compile('http://(.*?)/')

def getlimit(minutes=MINUTES):
  actual_time=datetime.today()
  delay=timedelta(seconds=minutes*60)
  return actual_time-delay

class RowParser(object):
  def __init__(self,row):
    self.row=row
    self.parsed=parser.search(row).groups()

  def get_ip(self):
    return self.parsed[0]

  def get_user(self):
    return self.parsed[1]

  def get_date(self):
    dd=self.parsed[2]
    try:
      dt=datetime.strptime(dd,'%d/%b/%Y:%H:%M:%S')
    except:
      dt=dd
    return dt

  def get_method(self):
    return self.parsed[3]
    
  def get_url(self):
    return self.parsed[4]

  def get_protocol(self):
    return self.parsed[5]

  def get_code(self):
    return self.parsed[6]

  def get_bytes(self):
    return self.parsed[7]
    
  def get_reffer(self):
    return self.parsed[8]

  def get_agent(self):
    return self.parsed[9]

  def get_latency(self):
    return self.parsed[10]

  def is_valid_line(row,https=[]):
    code=self.get_code()
    return (len(https)==0 or code in https)


def get_short_agent(agent):
  res=''
  dom=dom_pattern.findall(agent)
  if len(dom)>0:
    res=dom[0]
  else:
    eml=email_pattern.findall(agent)
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
  time_ft=int(time_ft)

  micros_time=int(time_ft%1000)
  time_ft=int(time_ft/1000)

  # return time in seconds.millisec
  return time_ft/1000.0

def change_format(dt):
  day,month,dd,tm,year=dt.split(' ')
  date=time.strptime('%s/%s/%s'%(dd,month,year),'%d/%b/%Y')
  return "%s %s.000000"%(time.strftime('%Y-%m-%d',date),tm)

def getparams(this):
  folder=logs
  script_name=this.split('/')[-1][:-3]
  full_path=os.path.realpath(__file__)
  real_name=full_path.split('/')[-1][:-3]
  parts=script_name.replace(real_name+'_','').split('_')
  title=parts[0]
  group=parts[1]
  filename="_".join(parts[2:])
  return full_path.replace('runner','worker'),title,title,'%s/%s'%(folder,filename)

