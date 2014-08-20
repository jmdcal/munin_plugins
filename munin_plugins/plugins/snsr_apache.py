#!/usr/bin/python2.7

"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'

import subprocess
import re
import sys
from collections import deque

from munin_plugins.utils import ApacheRowParser

from munin_plugins.plugins.plugin import Plugin

class Apache(Plugin):
  _prefix_name='snsr_apache'
  
  @property
  def _env(self):
    inherit_env=super(Apache,self)._env
    inherit_env.update({
      'title':'Apache',
      'group':'apache',
      'enabled':'LatencyAggregator,BotsCounter,HttpCodesCounter,SizeAggregator',
      'minutes':5,    
      'sub_plugins_folder':'www_analyzers',
      'sub_plugin_warning':10,
      'sub_plugin_critical':30,   
      'aggregate_warning':300,
      'aggregate_critical':1000,
    })
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
    parsed=[]
    for row in out.split('\n'):
      fnds=re.search(ptn,row)
      if fnds is not None:
        vh=re.search(ptn,row).group(1)
        if vh not in parsed:
          to_create=self._parse_title_and_customlog(vh)
          for title,access_log in to_create:
            inherit_env['title_%s'%a_file_no]=title
            inherit_env['access_%s'%a_file_no]=access_log
            a_file_no+=1
          parsed.append(vh)    
          
    return inherit_env
  
  def _parse_title_and_customlog(self,file_path):
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
    
    # For each class we store a list of tuples (vh_title, access_file, analyzer)    
    if len(files)<1:
      sys.stderr.write('Not configured: see documentation\n')
    else:   
      #loading sub plugins, a dict subp class -> (vh, access file, subp instance)
      results={}
      for name in self.getenv('enabled').split(','):
        try:
          results[self.get_sub_plugin(self.getenv('sub_plugins_folder'),name)]=deque()
        except:
          pass    
            
      for vhname,filename in files: 
        #read from files valid rows
        try:
          with open(filename,'r') as fi:
            currents=[cl() for cl in results]              
            for row in fi:
              datas=ApacheRowParser(row)
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
        print "multigraph apache_%s"%(cl.id)
        sitem=sorted(item)
        
        #calculating totals for current subplugin
        full=cl()
        for vhname,filename,an in sitem:   
          full=full+an
          
        if is_config:
          full.print_config_header(title)          
        full.print_data(printer,self.getenv('aggregate_warning'),self.getenv('aggregate_critical'))
        
        for vhname,filename,an in sitem:   
          print "multigraph apache_%s.%s"%(cl.id,filename.replace('/','_').replace('.','_').replace('-',''))
          if is_config:
            an.print_config_header(vhname)    
          an.print_data(printer,self.getenv('sub_plugin_warning'),self.getenv('sub_plugin_critical'))
          an.update_cache()

def main(argv=None,**kw):
  Apache().main()

if __name__ == '__main__':
  main()


