#DO NOT MODIFY THIS FILE ON WORKING INSTALLATION
#USE etc/custom.py TO OVERRIDE ALL VARIABLES

import re

#Daemons
NGINX_BASE='/etc/nginx'
NGINX_LOG='%s/logs' % NGINX_BASE
NGINX_SITES='%s/sites-enabled'%NGINX_BASE
NGINX_CONFD='%s/conf.d'%NGINX_BASE

MUNIN_BASE='/etc/munin'
MUNIN_PLUGINS_CONFD='%s/plugin-conf.d' % MUNIN_BASE
MUNIN_PLUGINS='%s/plugins' % MUNIN_BASE

#common 
CACHE="/var/cache/munin_plugins"

#utils.py
WRONG_AGENTS='%s/bad_signature'%CACHE
MINUTES=5
VALID_CTYPES=['text/html']
#Nginx log Format
#    log_format combined2 '$remote_addr - $remote_user [$time_local]  '
#                    '"$request" $status $body_bytes_sent '
#                    '"$http_referer" "$http_user_agent" [[$request_time]]';
#
# This is an example about the nginx log row
# 192.107.92.74 - - [25/Jun/2013:03:51:59 +0200]  "GET /++theme++enea-skinaccessibile/static/theme/styles/polaroid-multi.png HTTP/1.1" 499 0 "-" "Serf/1.1.0 mod_pagespeed/1.5.27.3-3005" [[2.554]]

_ip_pattern=r'^([0-9]+(?:\.[0-9]+){3})'
_user_pattern=r'\s+\-\s(.*?)'
_date_pattern=r'\s+\[([0-9]{2}\/[a-zA-Z]{3}\/[0-9\:]{13})\s\+[0-9]{4}\]'
_request_pattern=r'\s+\"([A-Z]*?)\s(.*?)(\sHTTP.*)?"'
_http_code_pattern=r'\s+([0-9]{3})'
_bytes_pattern=r'\s+([0-9]+)'
_reffer_pattern=r'\s+\"(.*?)\"'
_signature_pattern=r'\s+\"(.*?)\"'
_latency_pattern=r'\s+\[\[(.*)\]\]'

nginx_pattern= \
  _ip_pattern + \
  _user_pattern + \
  _date_pattern + \
  _request_pattern + \
  _http_code_pattern + \
  _bytes_pattern + \
  _reffer_pattern + \
  _signature_pattern


row_pattern=nginx_pattern+_latency_pattern #latency
NGINX_PARSER=re.compile(nginx_pattern)
ROW_PARSER=re.compile(row_pattern)

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

EMAIL_PARSER=re.compile("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}")
DOM_PARSER=re.compile('http://(.*?)(/|\))')

#generate.py
# check name -> (check string, return code)
REQUIREMENTS={
  'Python2.7':(['python2.7','-V'],0),
  'psutil':(['python2.7','-c','import psutil; print psutil.__version__'],0),
  'Monit':(['monit','-V'],0),
  'Munin node':(['munin-node-configure','--version',],1),
  'Nginx':(['nginx','-v'],0),
}


TMP_CONFIG='/tmp/_munin_plugins'
CONFIG_NAME='%s/munin_plugins'%MUNIN_PLUGINS_CONFD


#Bots.py
LOG_REGEX=r'(.*)access\.log$'
CACHE_BOTS="%s/bots"%CACHE
WL_AGENTS=re.compile('(mod_pagespeed)')

#worker_aggr.py
INTERVALS=(.5,1,2,5)    
LIMITS={'05':dict(w=500,c=1000),
        '1':dict(w=500,c=600), 
        '2':dict(w=40,c=50),  
        '5':dict(w=30,c=40),}

COLORS={
  '05':'00FF00',
  '1':'88FF00', 
  '2':'FFFF00',
  '5':'FF8800',
}

#worker_http.py
HTTP_CODES={
  400:"Bad Request",
  401:"Unauthorized",
  403:"Forbidden",
  444:"No Response for malware",
  500:"Internal Server Error",
  502:"Bad Gateway",
  503:"Service Unavailable",
  504:"Gateway Timeout",
}

#monit_downtime.py
MONIT_STATUS={
  "monit down":'757575',
  "running":'005000',
  "online with all services":'006000',
  "accessible":'007000',  
  "monitored":'008000',
  "initializing":'009000',
  "action done":'00A000', 
  "checksum succeeded":'00FF00',
  "connection succeeded":'00FF00',
  "content succeeded":'00FF00',
  "data access succeeded":'00FF00',
  "execution succeeded":'00FF00',
  "filesystem flags succeeded":'00FF00',
  "gid succeeded":'00FF00',
  "icmp succeeded":'00FF00',
  "monit instance changed not":'00FF00',
  "type succeeded":'00FF00',
  "exists":'FFFF00',
  "permission succeeded":'00FF00',
  "pid succeeded":'00FF00',
  "ppid succeeded":'00FF00',
  "resource limit succeeded":'00FF00',
  "size succeeded":'00FF00',
  "timeout recovery":'FFFF00',
  "timestamp succeeded":'00FF00',
  "uid succeeded":'00FF00',
  "not monitored":'00FFFF',
  "checksum failed":'FF0000',
  "connection failed":'0000FF',
  "content failed":'FF0000',
  "data access error":'FF0000',
  "execution failed":'FF0000',
  "filesystem flags failed":'FF0000',
  "gid failed":'FF0000',
  "icmp failed":'FF00FF',
  "monit instance changed":'FF0000',
  "invalid type":'FF0000',
  "does not exist":'FF0000',
  "permission failed":'FF0000',
  "pid failed":'FF0000',
  "ppid failed":'FF0000',
  "resource limit matched":'CCCC00',
  "size failed":'FF0000',
  "timeout":'FF0000',
  "timestamp failed":'FF0000',
  "uid failed":'FF0000',
}
MONIT_FIRSTS=[]
MONIT_LASTESTS=["accessible","online with all services","running","monit down"]
MONIT_RE=(
  r'^(Filesystem|Directory|File|Process|Remote Host|System|Fifo)'
  r"\s('.*?')"
  r'\s(.*)'
)
MONIT_PARSER=re.compile(MONIT_RE)
MONIT_PERCENTAGE_GRAPH=True #Use % values instead of absolute values
MONIT_FULL=False #Show all possible message instead all viewed message
CACHE_MONIT="%s/monit_messages"%CACHE
MONIT_OPTS=[]

#plone_usage
SYSTEM_VALUE_CACHE=('%s/system_state'%CACHE,'CachePickle')
SYSTEM_DEFAULTS=['cpu_times','memory_percent','connections','swap','storages','iocounters']

PLONE_GRAPHS={
  #'graph_id':(<title>,<cache file>,<id for system cache>,<psutil.proc_method>)
  'cpu_time':('cpu usage (%)','%s/zopeprocess'%CACHE,'cpu_times','get_cpu_times'),  
  'memory':('memory (%)',None,'memory_percent','get_memory_percent'),
  'connections':('connections',None,'connections','get_connections'), 
  'swap':('swap',None,'swap','get_memory_maps'),
  'storages':('file',None,'storages','get_open_files'),
  'io_counters':('I/O usage','%s/zopeios'%CACHE,'iocounters','get_io_counters'),
  'threads':('threads usage (%)','%s/zopethreads'%CACHE,'cpu_times','get_threads')
}

PLONE_GRAPHS_ORDER=['cpu_time','threads','memory_percent','swap','storages','io_counters','connections']


INSTANCES_CACHE='%s/zope_instances'%CACHE
AREASTACK_SENSORS=['cpu_time','memory_percent','swap','storages','threads']

#Leave this on the bottom

try:
  from custom import *
except ImportError:  
  pass
