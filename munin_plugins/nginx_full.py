#!/usr/bin/python2.7

import sys
from collections import deque

from munin_plugins.utils import *
from munin_plugins.nginx_analyzers import LatencyAggregator
from munin_plugins.nginx_analyzers import BotsCounter
from munin_plugins.nginx_analyzers import HttpCodesCounter
       
def main(argv=None, **kw):    
  argv=fixargs(argv)
  is_config=check_config(argv)
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
      full.print_data(printer,300,1000)
      
      for title,filename,an in sitem:   
        print "multigraph nginx_%s.%s"%(cl.id,filename.replace('/','_').replace('.','_').replace('-',''))
        if is_config:
          an.print_config_header()    
        an.print_data(printer,10,30)
        an.update_cache()
        
    
    
    









