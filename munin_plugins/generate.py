#!/usr/bin/python2.7

import re
import subprocess
from shutil import copy

from os import listdir
from os import symlink
from os import remove
from os.path import join
from os.path import sep
from os.path import exists
from os.path import isfile
from sys import prefix

from utils import fixargs
from etc.env import MUNIN_PLUGINS_CONFD
from etc.env import MUNIN_PLUGINS
from etc.env import NGINX_SITES
from etc.env import NGINX_LOG
from etc.env import REQUIREMENTS
from etc.env import TMP_CONFIG
from etc.env import CONFIG_NAME
from etc.env import CACHE

def check_requirements():
  for k in REQUIREMENTS:
    (v,retcode)=REQUIREMENTS[k]
    try:
      res=subprocess.check_output(v,stderr=subprocess.STDOUT)
      if res is None or len(res)==0:
        res='ok'
    except OSError:
      res='failed'
    except subprocess.CalledProcessError, err:
      # this is a way to solve a strange case of munin-node
      # if you call munin-node -V it returns state == 1 instead of 0
      res='failed'
      if err.returncode == retcode:
        res=err.output
    print "Checking %s: %s"%(k,res)
      
def get_real_file(file_log):
  res=None
  fn=file_log.split(sep)
  if exists(file_log):
    res=file_log
  elif exists(join(NGINX_LOG,file_log)):
    res=join(NGINX_LOG,file_log)
  elif len(fn)>0 and exists(join(NGINX_LOG,fn[-1])):
    res=join(NGINX_LOG,fn[-1])
  
  if res is not None:
     res=res.replace('%s%s'%(sep,sep),sep)
  return res

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
            access_log=get_real_file(access_log)
            if access_log is not None:
              res.append((title+'.'+port,access_log))
      elif 'listen' in row:
        port=row.replace('listen','').strip()
      elif re.match('^server_name\s',row):
        aliases=row.replace('server_name','').split()
        title=aliases[0]
      elif 'access_log' in row:
        access_log=row.strip().split()[1]
  return res
 
def create_link(orig,link):
  try:
    symlink(orig,link)
    print "CREATED: %s\n"%link
  except OSError:
    print "WARNING: %s\n"%link

#take from ./config/ a file to copy in /etc/munin/plugin-conf.d/
def config_env(fn,orig,dest):
  forig=join(orig,'config',fn)
  fdest=join(dest,fn)
  
  #checking if file exists
  if not isfile(fdest):
    copy(forig,fdest)

def install(fpy, syml,force_all,make_news):  
  orig=join(prefix,'bin',fpy)
  link=join(MUNIN_PLUGINS,syml)
  
  def_create=not exists(link)
  pars=dict(orig=orig,link=link)
  
  created=False
        
  if force_all:       
    create_link(orig=orig,link=link)  
    created=True
  elif make_news:
    if def_create:
      create_link(orig=orig,link=link)
      created=True
  else:
    if def_create:
      def_label='Y/n'
    else:
      def_label='y/N'

    ans=raw_input("Creates munin plugin %s -> %s [%s]?"%(syml,fpy,def_label))
    if (len(ans)==0 and def_create) or \
      (len(ans)>0 and ans.lower()=='y'):
      create_link(orig=orig,link=link)      
      created=True
      
  return created


def main(argv=None, **kw):
  argv=fixargs(argv)
  
  check_requirements()

  #do not make questions about creation but force all (-f option)
  force_all=False 
  #do not make questions about creation but force new ones (-n option)
  make_news=False
  #avoid symlinks creation
  help_asked=False
  if len(argv)>1:
    opts=argv[1:]
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
    #build config for nginx_*, they read from single file the list of access_logs
    tmp_file=open(TMP_CONFIG,'w')
    tmp_file.write('[nginx_*]\n')
    tmp_file.write('user root\n')
    tmp_file.write('group root\n')
    file_no=0
    
    for vh in listdir(NGINX_SITES):
      fpath=NGINX_SITES+'/'+vh
      if isfile(fpath):
        to_create=parse_title_and_customlog(fpath)
        for title,access_log in to_create:
          tmp_file.write('env.GRAPH_TITLE_%s %s\n'%(file_no,title))
          tmp_file.write('env.GRAPH_GROUP_%s %s\n'%(file_no,'nginx'))
          tmp_file.write('env.GRAPH_ACCESS_%s %s\n'%(file_no,access_log))
          file_no+=1

    tmp_file.close()
    if file_no>0:        
      created=install('nginx_full','nginx_full',force_all,make_news)
      if created:
        copy(TMP_CONFIG,CONFIG_NAME)  
      
    try:
      remove(TMP_CONFIG)
    except OSError:
      pass   
      
    created=install('plone_usage','plone_usage',force_all,make_news)
    if created:
      config_env('plone_usage',prefix,MUNIN_PLUGINS_CONFD)   

    created=install('monit_downtime','monit_downtime',force_all,make_news)
    if created:
      config_env('monit_downtime',prefix,MUNIN_PLUGINS_CONFD)   

if __name__ == '__main__':
  main()

