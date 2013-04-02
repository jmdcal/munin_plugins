#configuration file
from datetime import datetime,timedelta
import re
import time

#LogFormat from apache
#LogFormat "%h %l %u %t \"%r\" %>s %O \"%{Referer}i\" \"%{User-Agent}i\" <<%D,%>s,%{Content-Type}o>>" combined2
#185.184.3.196 - - [24/May/2012:06:43:40 +0200] "GET / HTTP/1.1" 200 5483 "-" "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET4.0C; .NET4.0E)" <<298502,200,text/html>>
#10.25.217.61 - - [24/May/2012:14:32:57 +0200] "GET /news/transito-sistpam-al-resia/phpmyadmin/sql.php3?server=000&cfgServers[000][host]=hello&btnDrop=No&goto=/etc/passwd HTTP/1.0" 404 14753 "http://ask.resia.aeronautica.difesa.it/news/transito-sistpam-al-resia" "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET4.0C; .NET4.0E)" <<825144,404,text/html>>

LAT_EXPR='\<\<[0-9]+'
DATE_EXPR='\[[0-9]{2}\/[a-zA-Z]{3}\/[0-9\:]{13}'
CTYPE_EXPR=',[a-z\/\-\.]*\>\>'
BYTES_EXPR='HTTP/[0-9\.]+\".?[0-9]{3}.?([0-9]*)'
CODE_EXPR='HTTP/[0-9\.]+\".?([0-9]{3})'
URL_EXPR='(GET|POST)\s(/.*?)\sHTTP'

MINUTES=5

VALID_CTYPES=['text/html']

LAT_SEARCHER=re.compile(LAT_EXPR)
DATE_SEARCHER=re.compile(DATE_EXPR)
CTYPE_SEARCHER=re.compile(CTYPE_EXPR)
BYTES_SEARCHER=re.compile(BYTES_EXPR)
CODE_SEARCHER=re.compile(CODE_EXPR)
URL_SEARCHER=re.compile(URL_EXPR)

def getlimit(minutes=MINUTES):
  actual_time=datetime.today()
  delay=timedelta(seconds=minutes*60)
  return actual_time-delay  

def get_from(row,searcher,strip=''):
  res=None
  exp=searcher.search(row)
  if exp is not None:
    val=exp.group(0)
    res=val.strip(strip)
  return res

def get_lat(row):
  return get_from(row,LAT_SEARCHER,'<>')

def get_date(row):
  date_parts=get_from(row,DATE_SEARCHER,'[]')
  try:
    dt=datetime.strptime(date_parts,'%d/%b/%Y:%H:%M:%S')
  except:
    dt=None
  return dt

def get_ctype(row):
  return get_from(row,CTYPE_SEARCHER,'<,>')

def get_bytes(row):
  bytes_part=BYTES_SEARCHER.search(row)
  bytes=0
  if bytes_part is not None:
    val_str=bytes_part.group(1)
    try:
      bytes=int(val_str)
    except ValueError:
      bytes=0
  return bytes

def get_code(row):
  code=0
  code_part=CODE_SEARCHER.search(row)
  if code_part is not None:
    val_str=code_part.group(1)
    try:
      code=int(val_str)
    except ValueError:
      code=0
  return code

def get_url(row):
  url=''
  url_match=URL_SEARCHER.search(row)
  if url_match is not None:
    url=url_match.group(2)
  return url

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

def is_valid_line(row,ctypes=[],https=[]):
  ctype=get_ctype(row)
  code=get_code(row)
  return (len(ctype)==0 or ctype in ctypes) and (len(https)==0 or code in https)
