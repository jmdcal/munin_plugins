#!/usr/bin/python2.7

# use at least 2.7 because Counter is not in previous versions

import re
import sys
import os

sys.path.append("..")

from etc.env import _ip_pattern
from etc.env import _user_pattern
from etc.env import _date_pattern
from etc.env import _request_pattern
from etc.env import _http_code_pattern
from etc.env import _bytes_pattern
from etc.env import _reffer_pattern
from etc.env import _signature_pattern
from etc.env import _latency_pattern

patterns=[
  (_ip_pattern,"Ip"),
  (_user_pattern,"User"),
  (_date_pattern,"Date"),
  (_request_pattern,"Req"),
  (_http_code_pattern,"Code"),
  (_bytes_pattern,"Bytes"),
  (_reffer_pattern,"Reffer"),
  (_signature_pattern,"Sign"),
  (_latency_pattern,"Lat"),
  ]


#row='127.0.0.1 - - [26/Jun/2013:11:52:14 +0200] "-" 400 0 "-" "-"'


if len(sys.argv)>1:
  row=sys.argv[1]
  fpat=r''
  flab=''
  for pat,lab in patterns:
    fpat=fpat+pat
    flab=flab+lab+'..'
    if re.match(fpat,row):
      print "%s ok"%flab
    else:
      print "%s FAIL"%flab
else:
  print "Usage: checklogrow.py '127.0.0.1 - - [26/Jun/2013:11:52:14 +0200] \"-\" 400 0 \"-\" \"-\"'  "  
  
  