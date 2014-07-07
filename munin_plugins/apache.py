#!/usr/bin/python2.7

import subprocess
import re
import sys
from collections import deque

from .utils import RowParser

from .plugin import Plugin
from .apache_analyzers import LatencyAggregator
from .apache_analyzers import BotsCounter
from .apache_analyzers import HttpCodesCounter

class Apache(Plugin):
  _title='Apache'
  _group='apache'
  _defaults={'enabled':'LatencyAggregator,BotsCounter,HttpCodesCounter','minutes':5} 
  

  def _apache_parse_title_and_customlog(self,file_path):
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

  
  def install(self,plugins_dir,plug_config_dir):  
    ans,def_create=self.ask('apache',plugins_dir)
    if (len(ans)==0 and def_create) or \
      (len(ans)>0 and ans.lower()=='y'):    

      print "Scanning Apache for VirtualHosts.."    
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
      envvars=self._defaults.copy()
      parsed=[]

      for row in out.split('\n'):
        fnds=re.search(ptn,row)
        if fnds is not None:
          vh=re.search(ptn,row).group(1)
          if vh not in parsed:
            to_create=self._apache_parse_title_and_customlog(vh)
            for title,access_log in to_create:
              print "..found %s [%s].."%(title,access_log)
              envvars['apache_title_%s'%a_file_no]=title
              envvars['apache_access_%s'%a_file_no]=access_log
              a_file_no+=1
            parsed.append(vh)
      print "..done."
      self.install_plugin('apache',plugins_dir,plug_config_dir,env=envvars)
    
    
  def get_files(self):
    logs=self.getenvs_with_id('apache_access_')
    titles=dict(self.getenvs_with_id('apache_title_'))
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
          #As shown in doc, %D option is in microseconds
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
        print "multigraph apache_%s"%(cl.id)
        sitem=sorted(item)
        full=cl('all',self._group)
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

def main(argv=None,**kw):
  Apache().main()

if __name__ == '__main__':
  main()


