#!/usr/bin/python2.7

import sys
from collections import deque
from os import listdir
from os.path import isfile
from os.path import sep

from .utils import *
from .nginx_analyzers import LatencyAggregator
from .nginx_analyzers import BotsCounter
from .nginx_analyzers import HttpCodesCounter
       
def install(plugins_dir,plug_config_dir):
  nginx_sites='/etc/nginx1'
  while not exists(nginx_sites):
    nginx_sites=raw_input('Insert a valid path for nginx virtualhosts config files [%s]'%nginx_sites)
   
  n_file_no=0
  extended={} 
  print "Scanning Nginx for VirtualHosts.."
  for vh in listdir(nginx_sites):
    fpath=nginx_sites+'/'+vh
    if isfile(fpath):
      to_create=_nginx_parse_title_and_customlog(fpath)
      for title,access_log in to_create:
        print "..found %s [%s].."%(title,access_log)
        extended['env.GRAPH_TITLE_%s'%n_file_no]=title
        extended['env.GRAPH_GROUP_%s'%n_file_no]='nginx'
        extended['env.GRAPH_ACCESS_%s'%n_file_no]=access_log
        n_file_no+=1
  print "..done."
  install_plugin('nginx_full',plugins_dir,plug_config_dir,extended)

def _nginx_parse_title_and_customlog(file_path):
  fd=open(file_path,'r')
  in_server=False
  res=[]
  for row in fd:
    if re.match('^#',row.strip()):
      pass #this is a comment    
    elif not in_server:
      if 'server {' in row:
        in_server=True
        title=''
        access_log=''
        port=''
        open_par=1
    else:
      row=row.strip().replace(';','')
      if '{' in row:
        open_par+=1
      elif '}' in row:
        open_par-=1
        if open_par==0:
          in_server=False
          if len(title)>0 and len(access_log)>0:
            res.append((title+'.'+port,access_log))
      elif 'listen' in row:
        port=row.replace('listen','').strip()
      elif re.match('^server_name\s',row):
        aliases=row.replace('server_name','').split()
        title=aliases[0]
      elif 'access_log' in row:
        access_log=row.strip().split()[1]
  return res       
       
def _get_real_file(file_log,base_log):
  res=None
  fn=file_log.split(sep)
  if exists(file_log):
    res=file_log
  elif exists(join(base_log,file_log)):
    res=join(base_log,file_log)
  elif len(fn)>0 and exists(join(base_log,fn[-1])):
    res=join(base_log,fn[-1])  
  if res is not None:
     res=res.replace('%s%s'%(sep,sep),sep)
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
        
if __name__ == '__main__':
  main()

    
    









