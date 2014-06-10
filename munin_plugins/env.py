import re
import ConfigParser
from os.path import join

from munin_plugins.base_info import NAME
from munin_plugins.base_info import EGG_CONFIG_DIR
from munin_plugins.base_info import EGG_CONFIG_MUNIN_DIR
from munin_plugins.base_info import EGG_CONFIG_NGINX_DIR
from munin_plugins.base_info import EGG_CACHE_DIR

from munin_plugins.base_info import SYS_VAR_PATH
from munin_plugins.base_info import SYS_CONFIG_MUNIN_DIR
from munin_plugins.base_info import SYS_CONFIG_NGINX_DIR
from munin_plugins.base_info import SYS_CACHE_DIR

CONFIG_FILE=join(SYS_VAR_PATH,'munin_plugins.conf')

#Defaults values overrideble from munin_plugins.conf
CACHE=SYS_CACHE_DIR
MINUTES=5

#Monit_downtime defaults overrideble from munin_plugins.conf
MONIT_PERCENTAGE_GRAPH=True
MONIT_FULL=False 

#Nginx_full defaults overrideble from munin_plugins.conf
NGINX_BASE='/etc/nginx'
NGINX_LOG='%s/logs' % NGINX_BASE
NGINX_SITES='%s/sites-enabled'%NGINX_BASE
NGINX_CONFD='%s/conf.d'%NGINX_BASE

#Apache 
APACHE_BASE='/etc/apache2'
APACHE_LOG='/var/log/apache2/'
APACHE_SITES='%s/sites-enabled'%APACHE_BASE
APACHE_CONF_EN='%s/conf-enabled'%APACHE_BASE
APACHE_CONF_AV='%s/conf-available'%APACHE_BASE

#Munin defaults overrideble from munin_plugins.conf
MUNIN_BASE='/etc/munin'
MUNIN_PLUGINS_CONFD='%s/plugin-conf.d' % MUNIN_BASE
MUNIN_PLUGINS='%s/plugins' % MUNIN_BASE

#Repmgr config file overrideble from munin_plugins.conf
REPMGR_CONF='/etc/repmgr.conf'

#Parsing munin_plugins.conf
config = ConfigParser.SafeConfigParser()
config.readfp(open(CONFIG_FILE))
for k,v in config.items('config'):
  try:
    vars()[k.upper()]=eval(v)
  except SyntaxError,NameError:
    vars()[k.upper()]=v
    
try:  
  for section in SECTIONS.split():
    for k,v in config.items(section):
      vars()[k.upper()]=v
  
except ConfigParser.NoOptionError as e:
  #This means there's no Sections specifications, we can live without
  pass

#Fixing Overrides
# -> Minutes needs to be a int
if isinstance(MINUTES,str):
  try:
    MINUTES=int(MINUTES)
  except ValueError:
    MINUTES=5
    

TMP_CONFIG='/tmp/_%s'%NAME
WRONG_AGENTS='%s/bad_signature'%CACHE
CACHE_BOTS="%s/bots"%CACHE
CACHE_APACHE_BOTS="%s/bots_apache"%CACHE
CACHE_MONIT="%s/monit_messages"%CACHE
SYSTEM_VALUE_CACHE=('%s/system_state'%CACHE,'CachePickle')
INSTANCES_CACHE='%s/zope_instances'%CACHE


JAVA_INSTANCES_CACHE='%s/java_instances'%CACHE
CONFIG_NAME='%s/munin_plugins'%MUNIN_PLUGINS_CONFD

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
NGINX_BYTES_RE=r'\s+([0-9]+)'
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

NGINX_LOG2_RE=NGINX_LOG_RE+NGINX_LATENCY_RE #latency

APACHE_LOG2_RE=NGINX_LOG_RE+NGINX_LATENCY_RE #latency

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

EMAIL_RE="[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"
DOM_RE='http://(.*?)(/|\))'

#generate.py
# check name -> (check string, return code)
REQUIREMENTS={
  'Python2.7':(['python2.7','-V'],0),
  'psutil':(['python2.7','-c','import psutil; print psutil.__version__'],0),
  'Monit':(['monit','-V'],0),
  'Munin node':(['munin-node-configure','--version',],1),
  'Nginx':(['nginx','-v'],0),
  'Repmgr':(['repmgr','--version'],0),
  'Apache':(['apachectl','-v'],0),
}

#*_analyzers/latencyaggregator.py
NLATENCY_INTERVALS=(.5,1,2,5)    
NLATENCY_LIMITS={
  '05':dict(w=500,c=1000),
  '1':dict(w=500,c=600), 
  '2':dict(w=40,c=50),  
  '5':dict(w=30,c=40),
}
NLATENCY_COLORS={
  '05':'00FF00',
  '1':'88FF00', 
  '2':'FFFF00',
  '5':'FF8800',
}
NLATENCY_CODES = [200,]

#*_analyzers/httpcodescounter.py
HTTP_CODES={
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
CACHE_HTTP_CODES="%s/httpcodes"%CACHE
CACHE_APACHE_HTTP_CODES="%s/httpcodes_apache"%CACHE
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

#plone_usage
SYSTEM_DEFAULTS=['cpu_times','virtual_memory','swap_memory','net_io_counters']
PSTORAGES_FILE_RE='.*((Data\.fs)|(\.log)).*'
JSTORAGES_FILE_RE=''

#repmgr
REPMGR_STATES=[('failed','FAILED','FF0000'),('master','master','00FF00'),('standby','standby','FFFF00')]


#RegEx Compilation
NGINX_PARSER=re.compile(NGINX_LOG_RE)
ROW_PARSER=re.compile(NGINX_LOG2_RE)
AROW_PARSER=re.compile(APACHE_LOG2_RE)
EMAIL_PARSER=re.compile(EMAIL_RE)
DOM_PARSER=re.compile(DOM_RE)
MONIT_PARSER=re.compile(MONIT_RE)
PSTORAGES_FILE_PARSER=re.compile(PSTORAGES_FILE_RE)
JSTORAGES_FILE_PARSER=re.compile(JSTORAGES_FILE_RE)
