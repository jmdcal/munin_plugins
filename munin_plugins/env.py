import re
import ConfigParser
from os.path import join
from sys import prefix

from .base_info import NAME

SYS_VAR_PATH=join(prefix,'var',NAME)

#Defaults values overrideble from munin_plugins.conf
CACHE=join(SYS_VAR_PATH,'cache')
MINUTES=5

    

WRONG_AGENTS='%s/bad_signature'%CACHE
CACHE_BOTS="%s/bots"%CACHE
CACHE_APACHE_BOTS="%s/bots_apache"%CACHE
SYSTEM_VALUE_CACHE=('%s/system_state'%CACHE,'CachePickle')
INSTANCES_CACHE='%s/zope_instances'%CACHE


JAVA_INSTANCES_CACHE='%s/java_instances'%CACHE

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
  'Munin node':(['munin-node-configure','--version',],1),
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

#plone_usage
SYSTEM_DEFAULTS=['cpu_times','virtual_memory','swap_memory','net_io_counters']
PSTORAGES_FILE_RE='.*((Data\.fs)|(\.log)).*'
JSTORAGES_FILE_RE=''


#RegEx Compilation
NGINX_PARSER=re.compile(NGINX_LOG_RE)
ROW_PARSER=re.compile(NGINX_LOG2_RE)
AROW_PARSER=re.compile(APACHE_LOG2_RE)
EMAIL_PARSER=re.compile(EMAIL_RE)
DOM_PARSER=re.compile(DOM_RE)
PSTORAGES_FILE_PARSER=re.compile(PSTORAGES_FILE_RE)
JSTORAGES_FILE_PARSER=re.compile(JSTORAGES_FILE_RE)
