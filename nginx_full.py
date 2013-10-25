#!/usr/bin/python2.7

import sys

from nginx_analyzers import LatencyAggregator
from nginx_analyzers import BotsCounter
from nginx_analyzers import HttpCodesCounter

from utils import *

def print_data(id,v):
  print "%s.value %s"%(id,v)

def print_config(id,v):
  print "%s.label %s"%(id,id)
                   
is_config=(len(sys.argv)>1 and sys.argv[1]=='config')
files=getparams_from_config()

limit=getlimit()

printer=print_data
if is_config:
  printer=print_config

analyzers=(LatencyAggregator,BotsCounter,HttpCodesCounter)

if len(files)<1:
  sys.stderr.write('Not configured: see documentation')
else:     
  for title,group,filename in files:
    #creates a list of analyzers
    an_objs=[cl(title,group) for cl in analyzers]
               
    #read from files valid rows
    fi=open(filename,'r')
    for row in fi:
      datas=RowParser(row)
      if datas.get_date()>limit:                      
        for an in an_objs:
          an.update_with(datas)
    fi.close()
  
    #prints
    for an in an_objs:
      print "multigraph nginx_%s_%s"%(an.id,filename.replace('/','_').replace('.','_'))
      if is_config:
        an.print_config_header()    
      an.print_data(printer)
      an.update_cache()
      
  
  
  









