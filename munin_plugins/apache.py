#!/usr/bin/python2.7

import subprocess
import re
import sys
from collections import deque

from os import listdir
from os.path import sep
from os.path import isfile

from .utils import *
from .apache_analyzers import LatencyAggregator
from .apache_analyzers import BotsCounter
from .apache_analyzers import HttpCodesCounter

def install(plugins_dir,plug_config_dir):  
  out=''
  try:
    #debian and derivated
    out=subprocess.check_output(['apachectl','-t','-D','DUMP_VHOSTS'],stderr=subprocess.STDOUT)
  except OSError:
    pass
  
  if len(out)<1:
    try:
      #RH and derivated
      out=subprocess.check_output(['httpd','-t','-D','DUMP_VHOSTS'],stderr=subprocess.STDOUT)
    except OSError:
      pass
      
  ptn='\((.*):(.*)\)'

  a_file_no=0
  extended={} 
  parsed=[]
  print "Scanning Apache for VirtualHosts.."
  for row in out.split('\n'):
    fnds=re.search(ptn,row)
    if fnds is not None:
      vh=re.search(ptn,row).group(1)
      if vh not in parsed:
        to_create=_apache_parse_title_and_customlog(vh)
        for title,access_log in to_create:
          print "..found %s [%s].."%(title,access_log)
          extended['env.GRAPH_TITLE_%s'%a_file_no]=title
          extended['env.GRAPH_GROUP_%s'%a_file_no]='apache'
          extended['env.GRAPH_ACCESS_%s'%a_file_no]=access_log
          a_file_no+=1
        parsed.append(vh)
  print "..done."
  install_plugin('apache',plugins_dir,plug_config_dir,extended)

def _apache_parse_title_and_customlog(file_path):
  fd=open(file_path,'r')
  in_virtualhost=False
  res=[]
  for row in fd:
    if re.match('^#',row.strip()) or len(row.strip())==0:
      pass #this is a comment    
    elif not in_virtualhost:
      if re.match('<VirtualHost (.*):(.*)>',row):
        in_virtualhost=True
        title='Default'
        access_log=''
        port=re.match('<VirtualHost (.*):(.*)>',row).group(2)
    else:
      row=row.strip()
      if re.match('</VirtualHost>',row):
        in_virtualhost=False
        if len(title)>0 and len(access_log)>0:
          res.append((title+'.'+port,access_log))
      elif re.match('^ServerName\s',row):        
        aliases=row.replace('ServerName','').split()
        title=aliases[0]
      elif re.match('^ServerAlias\s',row) and title=='Default':        
        aliases=row.replace('ServerAlias','').split()
        title=aliases[0]
      elif 'CustomLog' in row:
        access_log=row.strip().split()[1]
        
  return res

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
	#As shown in doc, %D option is in microseconds
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
      print "multigraph apache_%s"%(cl.id)
      sitem=sorted(item)
      full=cl('all','apache')
      for title,filename,an in sitem:   
        full=full+an
        
      if is_config:
        full.print_config_header()
      full.print_data(printer,300,1000)
      
      for title,filename,an in sitem:   
        print "multigraph apache_%s.%s"%(cl.id,filename.replace('/','_').replace('.','_').replace('-',''))
        if is_config:
          an.print_config_header()    
        an.print_data(printer,10,30)
        an.update_cache()

if __name__ == '__main__':
  main()


