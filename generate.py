#!/usr/bin/python

#Script generator
# see ./generate.sh -h for usage

import sys 
import os
import re
import subprocess
import shutil

from base64 import b16encode
from etc.env import MUNIN_PLUGINS_CONFD
from etc.env import MUNIN_PLUGINS
from etc.env import NGINX_SITES
from etc.env import NGINX_RUNNERS

conf_file=MUNIN_PLUGINS_CONFD
plugins_path=MUNIN_PLUGINS
sites_path=NGINX_SITES

#get list of runner
runners_custom=NGINX_RUNNERS

def parse_title_and_customlog(file_path):
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
      elif re.match('^server_name',row):
        aliases=row.replace('server_name','').split()
        title=aliases[0]
      elif 'access_log' in row:
        access_log=row.strip().split()[1]
  return res

def create_full_link_name(runner,title,customlog,path):
  name,ext=runner.split('.')
  log_file=b16encode(customlog.split('/')[-1])
  title=b16encode(title)
  link_name="%s_%s_nginx_%s"%(name,title,log_file)
  link_name=link_name.replace('.','#')
  return '/'.join([path,link_name])
 
def create_link(orig,link):
  try:
    os.symlink(orig,link)
    print "CREATED: %s\n"%link
  except OSError:
    print "WARNING: %s\n"%link

def config_env(fn,orig,dest):
  forig='/'.join([orig,'config',fn])
  fdest='/'.join([dest,fn])
  
  #checking if file exists
  if not os.path.isfile(fdest):
    shutil.copy(forig,fdest)

def install(force_all,make_news,def_create,fun,pars={}):
  created=False
  if force_all:       
    fun(**pars)  
    created=True
  elif make_news:
    if def_create:
      fun(**pars)
      created=True
  else:
    if def_create:
      def_label='Y/n'
    else:
      def_label='y/N'

    print "\n\n"
    for k,v in pars.items():
      print "-->%s: %s"%(k,v)
       
    ans=raw_input("\nCreates munin plugin [%s]?"%def_label)
    if (len(ans)==0 and def_create) or \
      (len(ans)>0 and ans.lower()=='y'):
      fun(**pars)      
      created=True
      
  return created

created=False
#do not make questions about creation but force all (-f option)
force_all=False 
#do not make questions about creation but force new ones (-n option)
make_news=False
#avoid symlinks creation
help_asked=False
if len(sys.argv)>1:
  opts=sys.argv[1:]
  if '-f' in opts:
    force_all=True
  elif '-n' in opts:
    make_news=True
  elif '-h' in opts or '--help' in opts:
    help_asked=True
    print 'USAGE:\n\tgenerate.py [opts]\n'
    print '  Options:'
    print '\t-h, --help:\tshow this help'
    print '\t-f:\t\tforce creation of all symlinks without asking'
    print '\t-n:\t\tforce creation of new symlinks without asking'
    
if not help_asked:   
  orig_name='/'.join([os.getcwd(),'plone_usage.py'])
  link_name='/'.join([plugins_path,'plone_usage'])
  def_create=not os.path.exists(link_name)
  pars=dict(orig=orig_name,link=link_name)
    
  created=install(force_all,make_news,def_create,create_link,pars)
  if created:
    config_env('plone_usage',os.getcwd(),MUNIN_PLUGINS_CONFD)   
  
  orig_name='/'.join([os.getcwd(),'monit_downtime.py'])
  link_name='/'.join([plugins_path,'monit_downtime'])
  def_create=not os.path.exists(link_name)
  pars=dict(orig=orig_name,link=link_name)
    
  created=install(force_all,make_news,def_create,create_link,pars)
  if created:
    config_env('monit_downtime',os.getcwd(),MUNIN_PLUGINS_CONFD)   
  
  #configure plugins that use runner
  #foreach virtualhost file in sites_path
  created=False
  for vh in os.listdir(sites_path):
    fpath=sites_path+'/'+vh
    if os.path.isfile(fpath):
      to_create=parse_title_and_customlog(fpath)
      for title,access_log in to_create:
        for runner in runners_custom: 
          orig_name='/'.join([os.getcwd(),runner])
          link_name=create_full_link_name(runner,title,access_log,plugins_path)
          print "%s %s %s"%(title,access_log,link_name)
          def_create=not os.path.exists(link_name)        
          pars=dict(orig=orig_name,link=link_name)        
          created=install(force_all,make_news,def_create,create_link,pars) or created
        
  if created:
    config_env('runners',os.getcwd(),MUNIN_PLUGINS_CONFD)

