#

#common 
logs='/var/log/nginx/'

#utils.py
MINUTES=5
VALID_CTYPES=['text/html']

#Bots.py
log_regex=r'(.*)access\.log$'
cache="/opt/munin_plugins/cache/bots"
wl_agents=re.compile('(mod_pagespeed)')

#worker_aggr.py
INTERVALS=(.5,1,2,5)    
limits={'05':dict(w=500,c=1000),
        '1':dict(w=500,c=600), 
        '2':dict(w=40,c=50),  
        '5':dict(w=30,c=40),}

colors={
  '05':'00FF00',
  '1':'88FF00', 
  '2':'FFFF00',
  '5':'FF8800',
}

