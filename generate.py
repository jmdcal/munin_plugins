#!/usr/bin/python

#Script generator
# generate.py [<munin plugins conf file> <munin plugins path> <path_sites_nginx>]
#
# example:
# generate.py /etc/munin/plugin-conf.d/munin-node /etc/munin/plugins /etc/nginx/sites-enabled


import sys 
import os
import re
from base64 import b16encode
from etc.env import MUNIN_PLUGINS_BLOCK
from etc.env import MUNIN_PLUGINS_CONF
from etc.env import MUNIN_PLUGINS
from etc.env import NGINX_SITES
from etc.env import NGINX_RUNNERS

title_munin_block=MUNIN_PLUGINS_BLOCK
conf_file=MUNIN_PLUGINS_CONF
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
      row=row.replace(';','')
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
      elif 'server_name' in row:
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
  return path+'/'+link_name

def create_runner(runner,link_name):    
  try:    
    os.symlink(os.getcwd()+"/"+runner,link_name)
    print "CREATED: %s"%link_name
  except OSError:
    print "WARNING: %s"%link_name

#foreach virtualhost file in sites_path
for vh in os.listdir(sites_path):
  to_create=parse_title_and_customlog(sites_path+'/'+vh)
  for title,access_log in to_create:
    for runner in runners_custom:
  
      link_name=create_full_link_name(runner,title,access_log,plugins_path)
      
      if not os.path.exists(link_name):
        def_create=True
        def_label='Y/n'
      else:
        def_create=False
        def_label='y/N'
      
      ans=raw_input("\n--> %s\n\t- %s\n\t- %s\n\t- %s\nCreates munin plugin [%s]?"%(vh,title,access_log,link_name,def_label))
      if (len(ans)==0 and def_create) or \
         (len(ans)>0 and ans.lower()=='y'):
        create_runner(runner,link_name)


#add rights in config file_path
fo=open(conf_file,'r')
is_ok=False
for row in fo:
  if title_munin_block in row:    
    is_ok=True
  else:
    print "%s in %s FAILS" % (title_munin_block, row)
fo.close()

if not is_ok:
  fo=open(conf_file,'a')
  fo.write("\n"+title_munin_block+"\nuser root\ngroup root\ntimeout 120\n\n")

