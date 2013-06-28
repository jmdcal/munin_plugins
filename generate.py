#!/usr/bin/python

#Script generator
# generate.py [<munin plugins conf file> <munin plugins path> <path_sites_nginx>]
#
# example:
# generate.py /etc/munin/plugin-conf.d/munin-node /etc/munin/plugins /etc/nginx/sites-enabled


import sys 
import os

title_munin_block='[runner_*]'

def parse_title_and_customlog(file_path):
  fd=open(file_path,'r')
  in_server=False
  res=[]
  for row in fd:
    if not in_server:
      if 'server {' in row:
        in_server=True
        title=''
        access_log=''
        port=''
        open_par=1
    else:
      if '{' in row:
        open_par+=1
      elif '}' in row:
        open_par-=1
        if open_par==0:
          in_server=False
        if len(title)>0 and len(access_log)>0:
          res.append((title+'.'+port,access_log,error_log))
      if 'listen' in row:
        port=row.replace('listen','').strip()
      elif 'server_name' in row:
        title=row.replace('server_name','').strip()
      elif 'access_log' in row:
        access_log=row.strip().split(' ')[1]
  return res

def create_runner(runner,title,customlog,path):
  name,ext=runner.split('.')
  log_file=customlog.split('/')[-1]
  link_name="%s_%s_nginx_%s.%s"%(name,title,log_file,ext)
  try:
    os.symlink(os.getcwd()+"/"+runner,path+'/'+link_name)
    print path+'/'+link_name

  except OSError:
    print "WARNING: %s"%link_name

if len(sys.argv)>3:
  conf_file=sys.argv[1]
  plugins_path=sys.argv[2]
  sites_path=sys.argv[3]
else:
  conf_file='/etc/munin/plugin-conf.d/munin-node'
  plugins_path='/etc/munin/plugins'
  sites_path='/etc/nginx/sites-enabled'

#get list of runner
runners_custom=['runner_aggr.py','runner_http.py',]
runners_error=[]

#foreach virtualhost file in sites_path
for vh in os.listdir(sites_path):
  to_create=parse_title_and_customlog(sites_path+'/'+vh)
  for title,access_log,error_log in to_create:
    ans=raw_input("%s\n%s\n%s\nCreates munin plugin [Y/n]?"%(title,access_log,error_log))
    if ans=='y' or len(ans)<1:
      if len(title)>0 and len(access_log)>0:
        for runner in runners_custom:
          create_runner(runner,title,access_log,plugins_path)
      if len(title)>0 and len(error_log)>0:
        for runner in runners_error:
          create_runner(runner,title,error_log,plugins_path)


#add rights in config file_path
fo=open(conf_file,'r')
is_ok=False
for row in fo:
  if title_munin_block in row:
    is_ok=True
fo.close()

fo=open(conf_file,'a')
fo.write("\n"+title_munin_block+"\nuser root\ngroup root\ntimeout 120\n\n")

