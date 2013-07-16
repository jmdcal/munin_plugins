#
import re

#common 
LOGS='/opt/nginx/logs/'
CACHE="/opt/munin_plugins/cache"

#utils.py
MINUTES=5
VALID_CTYPES=['text/html']
#Nginx log Format
#    log_format combined2 '$remote_addr - $remote_user [$time_local]  '
#                    '"$request" $status $body_bytes_sent '
#                    '"$http_referer" "$http_user_agent" [[$request_time]]';
#
# This is an example about the nginx log row
# 192.107.92.74 - - [25/Jun/2013:03:51:59 +0200]  "GET /++theme++enea-skinaccessibile/static/theme/styles/polaroid-multi.png HTTP/1.1" 499 0 "-" "Serf/1.1.0 mod_pagespeed/1.5.27.3-3005" [[2.554]]
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
ROW_PARSER=re.compile(row_pattern)

# row_pattern produce:
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
# so row_mapping is the follow
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

