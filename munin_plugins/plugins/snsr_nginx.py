#!/usr/bin/python2.7

import sys
import re

from collections import deque

from os import listdir
from os.path import isfile
from os.path import exists
from os.path import join

from munin_plugins.utils import NginxRowParser

from munin_plugins.plugins.plugin import Plugin
from munin_plugins.plugins.www_analyzers import LatencyAggregator
from munin_plugins.plugins.www_analyzers import BotsCounter
from munin_plugins.plugins.www_analyzers import HttpCodesCounter
from munin_plugins.plugins.www_analyzers import SizeAggregator
       
class Nginx(Plugin):
  _prefix_name='snsr_nginx'
  
  @property
  def _env(self):
    inherit_env=super(Nginx,self)._env
    inherit_env.update({
      'title':'Nginx',
      'group':'nginx',
      'enabled':'LatencyAggregator,BotsCounter,HttpCodesCounter,SizeAggregator',
      'minutes':5,
      'sub_plugins_folder':'www_analyzers',
    })

    n_file_no=0
    parsed=[]      
    vh_base='/etc/nginx/sites-enabled'
    try:
      for vh in listdir(vh_base):
        fpath=join(vh_base,vh)
        if isfile(fpath) and vh not in parsed:
          to_create=self._parse_title_and_customlog(fpath)
          for title,access_log in to_create:
            inherit_env['title_%s'%n_file_no]=title
            inherit_env['access_%s'%n_file_no]=access_log
            n_file_no+=1
          parsed.append(vh)
    except OSError:
      pass
      
    return inherit_env
    
  def _parse_title_and_customlog(self,file_path):
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
          tmp=row.strip().split()[1]
          if 'off' not in tmp:
            access_log=tmp
    return res       
       
  def get_files(self):
    logs=self.getenv_prefix_with_id('access_')
    titles=dict(self.getenv_prefix_with_id('title_'))
    return [(titles.get(id,'undef'),ff) for id,ff in logs]            
       
  def main(self,argv=None, **kw):    
    files=self.get_files()
    
    is_config=self.check_config(argv)
    title=self.getenv('title') 
    limit=self.getlimit(self.getenv('minutes'))
    
    printer=self.print_data
    if is_config:
      printer=self.print_config

    # For each class we store a list of tuples (title,analyzer)
    if len(files)<1:
      sys.stderr.write('Not configured: see documentation\n')
    else: 
      #loading sub plugins, a dict subp class -> (vh, access file, subp instance)
      results={}
      for name in self.getenv('enabled').split(','):
        try:
          results[eval(name)]=deque()
        except:
          pass  
      
      for vhname,filename in files: 
        #read from files valid rows
        try:
          with open(filename,'r') as fi:
            currents=[cl() for cl in results]              
            for row in fi:
              datas=NginxRowParser(row)
              if datas.get_date() is not None and datas.get_date()>limit:                      
                #updating current vh data
                for sb in currents:
                  sb.update_with(datas)                  
            
            #store current 
            for sb in currents:
              results[sb.__class__].append((vhname,filename,sb))            
        except IOError:
          sys.stderr.write('NotExists: file %s not exists!\n'%filename)      
          
      #prints
      for cl,item in results.items():    
        print "multigraph nginx_%s"%(cl.id)
        sitem=sorted(item)
        
        #calculating totals for current subplugin
        full=cl()
        for title,filename,an in sitem:   
          full=full+an
          
        if is_config:
          full.print_config_header(title)
        full.print_data(printer,300,1000)
        
        for title,filename,an in sitem:   
          print "multigraph nginx_%s.%s"%(cl.id,filename.replace('/','_').replace('.','_').replace('-',''))
          if is_config:
            an.print_config_header(title)    
          an.print_data(printer,10,30)
          an.update_cache()

def main(argv=None,**kw):
  Nginx().main()
        
if __name__ == '__main__':
  main()

    
    









