"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'

from datetime import datetime
import re

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
    
