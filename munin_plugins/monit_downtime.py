#!/usr/bin/python2.7

import re  

import subprocess

from .plugin import Plugin

from .utils import CacheCounter

from .env import CACHE

MONIT_STATUS={
  "monit down":'757575',
  "running":'005000',
  "online with all services":'006000',
  "accessible":'007000',  
  "monitored":'008000',
  "initializing":'009000',
  "action done":'00A000', 
  "checksum succeeded":'00FF00',
  "connection succeeded":'00FF00',
  "content succeeded":'00FF00',
  "data access succeeded":'00FF00',
  "execution succeeded":'00FF00',
  "filesystem flags succeeded":'00FF00',
  "gid succeeded":'00FF00',
  "icmp succeeded":'00FF00',
  "monit instance changed not":'00FF00',
  "type succeeded":'00FF00',
  "exists":'FFFF00',
  "permission succeeded":'00FF00',
  "pid succeeded":'00FF00',
  "ppid succeeded":'00FF00',
  "resource limit succeeded":'00FF00',
  "size succeeded":'00FF00',
  "timeout recovery":'FFFF00',
  "timestamp succeeded":'00FF00',
  "uid succeeded":'00FF00',
  "not monitored":'00FFFF',
  "checksum failed":'FF0000',
  "connection failed":'0000FF',
  "content failed":'FF0000',
  "data access error":'FF0000',
  "execution failed":'FF0000',
  "filesystem flags failed":'FF0000',
  "gid failed":'FF0000',
  "icmp failed":'FF00FF',
  "monit instance changed":'FF0000',
  "invalid type":'FF0000',
  "does not exist":'FF0000',
  "permission failed":'FF0000',
  "pid failed":'FF0000',
  "ppid failed":'FF0000',
  "resource limit matched":'CCCC00',
  "size failed":'FF0000',
  "timeout":'FF0000',
  "timestamp failed":'FF0000',
  "uid failed":'FF0000',
}

MONIT_PARSER=re.compile((
  r'^(Filesystem|Directory|File|Process|Remote Host|System|Fifo)'
  r"\s('.*?')"
  r'\s(.*)'
))

class Monit(Plugin):
  _title='Monit status'
  _group='monit'
  _defaults={'cache':"%s/monit_messages"%CACHE,
             'percentage':'True',
             'full':'False',
             'lastest':"accessible,online with all services,running,monit down",}

  def populate_vals(self):
    to_init=['monit down',]
    status=self.getenvs('monit_state_')
    if self.getenv('full'):
      to_init+=status.keys()
    counts=CacheCounter(self.getenv('cache'))
    for i in to_init:
      counts[i]=0
    return counts
  
  def print_config(self):
    vals=self.populate_vals()
    print "graph_title %s"%self._title
    print "graph_args --base 1000"
    print "graph_vlabel status"
    print "graph_category %s"%self._group
    print "graph_order %s" % " ".join(self.graph_order(vals))
    status={}
    try:
      status=dict(self.getenvs('monit_state_'))
    except:
      pass
    for l in vals:
      #get color if available
      c=status.get(l,None)
      id=l.strip().replace(' ','_')
      print "%s.label %s" % (id,l)
      print "%s.draw AREASTACK" % id
      if c is not None:
        print "%s.colour %s"  % (id,c)

  def graph_order(self,alls):
    post=self.getenv('lastest').split(',')    
    middle=[i for i in alls if i not in post]  
    return [i.strip().replace(' ','_') for i in  middle+post]

    
  def install(self,plugins_dir,plug_config_dir):
    ans,def_create=self.ask('monit_downtime',plugins_dir)
    if (len(ans)==0 and def_create) or \
      (len(ans)>0 and ans.lower()=='y'):    
      
      envvars=self._defaults.copy()               
      for pos,(lab,col) in enumerate(MONIT_STATUS.items()):
        envvars['monit_state_%s'%pos]="%s,%s"%(lab,col)
    
      self.install_plugin('monit_downtime',plugins_dir,plug_config_dir,env=envvars)
  
  def parse_monit_row(self,row):
    status=None
    try:
      groups=MONIT_PARSER.match(row).groups()
    except AttributeError:
      pass
    else:
      status=groups[2].lower().strip()
    return status
  
  def main(self,argv=None, **kw): 
    if self.check_config(argv):
      self.print_config()
    else:  
      counts=self.populate_vals()
      if len(counts)==0:
        sys.stderr.write('Not configured: see documentation\n')
      else:
        csensors=1
        try:
          pid=int(subprocess.check_output(['pidof','monit'],stderr=subprocess.STDOUT).strip())
        except (subprocess.CalledProcessError, ValueError):
          #if fails means that the process is not running
          counts['monit down']=1
        else:
          csensors=0
          sensors=subprocess.check_output(['monit','summary'],stderr=subprocess.STDOUT)
          for row in sensors.split('\n'):
            status=self.parse_monit_row(row)
            if status is not None:
              counts[status]=counts[status]+1
              csensors+=1

        norm=lambda x:x
        if self.getenv('percentage'):
          norm=lambda x:(x*100/csensors)
          
        for l,v in counts.items():
          id=l.replace(' ','_')
          print "%s.value %s"% (id,norm(v))
            
        counts.store_in_cache()
  

def main(argv=None, **kw): 
  Monit().main()

if __name__ == '__main__':
  main()



