#!/usr/bin/python2.7

import sys
from collections import deque

from nginx_analyzers import LatencyAggregator
from nginx_analyzers import BotsCounter
from nginx_analyzers import HttpCodesCounter

from utils import *
                   
is_config=(len(sys.argv)>1 and sys.argv[1]=='config')
files=getparams_from_config()

limit=getlimit()

printer=print_data
if is_config:
  printer=print_config

analyzer_classes=(LatencyAggregator,BotsCounter,HttpCodesCounter)

# For each class we store a list of tuples (title,analyzer)
results=dict([(cl,deque()) for cl in analyzer_classes])

if len(files)<1:
  sys.stderr.write('Not configured: see documentation')
else:     
  for title,group,filename in files:
    #creates a list of analyzers
    an_objs=[cl(title,group) for cl in analyzer_classes]
               
    #read from files valid rows
    fi=open(filename,'r')
    for row in fi:
      datas=RowParser(row)
      if datas.get_date()>limit:                      
        for an in an_objs:
          an.update_with(datas)
    fi.close()
   
    #store 
    for an in an_objs:
      results[an.__class__].append((title,filename,an))
      
  #prints
  for cl,item in results.items():    
    print "multigraph nginx_%s"%(cl.id)
    sitem=sorted(item)
    full=cl('all','nginx')
    for title,filename,an in sitem:   
      full=full+an
      
    if is_config:
      full.print_config_header()
    full.print_data(printer)
    
    for title,filename,an in sitem:   
      print "multigraph nginx_%s.%s"%(cl.id,filename.replace('/','_').replace('.','_').replace('-',''))
      if is_config:
        an.print_config_header()    
      an.print_data(printer)
      an.update_cache()
      
  
  
  









