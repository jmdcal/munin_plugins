#!/usr/bin/python2.7

import sys
import re

from collections import deque

from os import listdir
from os.path import isfile
from os.path import exists

from .utils import RowParser

from .plugin import Plugin
from .nginx_analyzers import LatencyAggregator
from .nginx_analyzers import BotsCounter
from .nginx_analyzers import HttpCodesCounter
       
       
class Nginx(Plugin):
  _title='Nginx'
  _group='nginx'
  _defaults={'enabled':'LatencyAggregator,BotsCounter,HttpCodesCounter','minutes':5} 
  
  def _nginx_parse_title_and_customlog(self,file_path):
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
              
  def install(self,plugins_dir,plug_config_dir):
    ans,def_create=self.ask('nginx_full',plugins_dir)
    if (len(ans)==0 and def_create) or \
      (len(ans)>0 and ans.lower()=='y'):
      nginx_sites='/etc/nginx'
      n_file_no=0
      
      while n_file_no==0:
        np=raw_input('Insert a valid path for nginx virtualhosts config files [%s]'%nginx_sites)
        if np is not None and len(np)>0:
          nginx_sites=np
       
        envvars=self._defaults.copy()
        print "Scanning Nginx for VirtualHosts.."
        for vh in listdir(nginx_sites):
          fpath=nginx_sites+'/'+vh
          if isfile(fpath):
            to_create=self._nginx_parse_title_and_customlog(fpath)
            for title,access_log in to_create:
              print "..found %s [%s].."%(title,access_log)
              envvars['nginx_title_%s'%n_file_no]=title
              envvars['nginx_access_%s'%n_file_no]=access_log
              n_file_no+=1
        if n_file_no==0:
          print "No valid configuration found... try again."
        else:
          print "..done."
      self.install_plugin('nginx_full',plugins_dir,plug_config_dir,env=envvars)              
       
  def get_files(self):
    logs=self.getenvs_with_id('nginx_access_')
    titles=dict(self.getenvs_with_id('nginx_title_'))
    return [(titles.get(id,'undef'),ff) for id,ff in logs]            
       
  def main(self,argv=None, **kw):    
    files=self.get_files()
    
    is_config=self.check_config(argv)
    
    limit=self.getlimit(self.getenv('minutes'))
    
    printer=self.print_data
    if is_config:
      printer=self.print_config

    analyzer_classes=[]
    results={}
    for name in self.getenv('enabled').split(','):
      try:
        cl=eval(name)
        analyzer_classes.append(cl)
        results[cl]=deque()
      except:
        pass

    # For each class we store a list of tuples (title,analyzer)

    if len(files)<1:
      sys.stderr.write('Not configured: see documentation\n')
    else:     
      for title,filename in files:
        #creates a list of analyzers
        an_objs=[cl(title,self._group) for cl in analyzer_classes]
                                
        #read from files valid rows
        try:
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
        except IOError:
          sys.stderr.write('NotExists: file %s not exists!\n'%filename)
          
      #prints
      for cl,item in results.items():    
        print "multigraph nginx_%s"%(cl.id)
        sitem=sorted(item)
        full=cl('all',self._group)
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

def main(argv=None,**kw):
  Nginx().main()
        
if __name__ == '__main__':
  main()

    
    









