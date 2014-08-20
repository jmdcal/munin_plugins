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

import psutil
import re
from collections import deque

from munin_plugins.plugins.plugin import Plugin

from munin_plugins.utils import CachePickle
from munin_plugins.utils import CacheDict

from munin_plugins.env import CACHE

class Processes(Plugin):
  _prefix_name='snsr_processes'
  
  @property
  def _env(self):
    inherit_env=super(Processes,self)._env
    inherit_env.update({
      'title':'Processes',
      'group':'processes',
      'enabled':'cpu_usage_snsr,memory_snsr,connections_snsr,swap_snsr,storages_snsr,io_counters_snsr,io_counters_abs_snsr,threads_snsr',
      'system_defaults':'cpu_times,virtual_memory,swap_memory,net_io_counters',
      'show_jboss':True,
      'show_catalina':True,
      'show_plone':True,
      'system_cache':'%s/system_state'%CACHE,
      'instance_cache':'%s/process_instances'%CACHE,
      'sub_plugins_folder':'processes_analyzers',
    })
    return inherit_env
    
  @property
  def _common(self):
    inherit_common=super(Processes,self)._common
    inherit_common.update({
      'timeout':120,
    })
    return inherit_common
          
  def main(self,argv=None, **kw):     
    is_config=self.check_config(argv)
    title=self.getenv('title')
    group=self.getenv('group')

    printer=self.print_data
    if is_config:
      printer=self.print_config

    sys_prev,sys_curr=self.load_sys(self.getenv('system_defaults').split(','))  
    ps_cache=self.load_process()
    
    analyzer_classes=[]
    for name in self.getenv('enabled').split(','):
      try:
        analyzer_classes.append(self.get_sub_plugin(self.getenv('sub_plugins_folder'),name))
      except (KeyError,ImportError) as e:        
        pass
    
    for cl in analyzer_classes:
      sensor=cl(sys_prev,sys_curr)

      print "multigraph processes_%s"%cl.__name__
      if is_config:
        print "graph_title %s %s"%(title,sensor.getenv('subtitle'))    
        print "graph_args --base 1000"
        print "graph_vlabel %s"%sensor.getenv('label')
        print "graph_category %s"%group
      
      graph=sensor.graphType()
      for name,pd in ps_cache.items():  
        ids="%s_%s"%(name,cl.__name__)
        curr_value=getattr(pd,sensor.proc_mtd,lambda : None)()    
        
        res=sensor.calculate(name,curr_value)

        if isinstance(res,int) or isinstance(res,float):
          printer(id=ids,
                  value=res,
                  label=name,
                  draw=graph)
        elif isinstance(res,list) or isinstance(res,deque) or isinstance(res,set):
          for fd,row in res:
            printer(id='%s-%s'%(ids,fd),
                    value=row,
                    label='%s %s '%(name,fd),
                    draw=graph)        
      if not is_config:        
        sensor.store_in_cache()

    if not is_config:    
      #align prev with curr
      for k,v in sys_curr.items():    
        sys_prev[k]=v
      #store in the file
      sys_prev.store_in_cache()
      ps_cache.store_in_cache();

  def load_sys(self,defaults):
    cpath=self.getenv('system_cache')
   
    #Fetch from cache
    try:
      system_cache=CachePickle(cpath)
    except NameError:
      system_cache=None
    sys_curr={}
    
    for k in defaults:      
      sys_curr[k]=self.namedtuple2dict(getattr(psutil,k,lambda : None)())
      try:
        system_cache[k]
      except KeyError:  
        system_cache[k]=sys_curr[k]
    return system_cache,sys_curr
  
  def find_cfg(self,command):
    cfg=None
    for i in command:
      if 'zope.conf' in i or 'zeo.conf' in i:
        cfg=i     
    return cfg

  def build_sensor_name_plone(self,command):
    cfg=self.find_cfg(command)
    name=None
    if cfg is not None:
      try:
        instance=re.search('parts/(.*?)/etc',cfg).group(1)
        buildout=re.search('/(.*?)/parts',cfg).group(1)
      except AttributeError:
        pass
      else:
        path=buildout.split('/')
        name=path[-1]
        if name=='buildout':
          name=path[-2]
        name='%s_%s'%(name,instance)        
    return name

  def build_sensor_name_jboss(self,command):
    name=None
    plain=" ".join(command)
    if 'bin/java' in plain and 'org.jboss.Main' in plain:
        name='org.jboss.Main'    
    return name

  def build_sensor_name_catalina(self,command):
    name=None
    plain=" ".join(command)
    if 'bin/java' in plain and 'Bootstrap' in plain:
        name='catalina.startup.Bootstrap'    
    return name

  def build_sensor_name(self,command):
    name=None
    
    if self.getenv('show_plone'):
      name=self.build_sensor_name_plone(command)
      
    if self.getenv('show_jboss') and name is None:
      name=self.build_sensor_name_jboss(command)
      
    if self.getenv('show_catalina') and name is None:
      name=self.build_sensor_name_catalina(command)
      
    if name is not None:
      name=name.replace(".","_")
    
    return name

  def load_process(self):
    cache=CacheDict(self.getenv('instance_cache'),def_value=None)
    for pd in psutil.process_iter(): 
      name=self.build_sensor_name(pd.cmdline())
      #ppid>1 means that is a child: this check is useful for zeo process 
      if name is not None and pd.ppid>1:
        cache[name]=pd
    return cache

def main(argv=None,**kw):
  Processes().main()
        
if __name__ == '__main__':
  main()

