"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'

import sys

from os.path import join
from os.path import exists
from os import symlink

from datetime import datetime
from datetime import timedelta

from math import log

from munin_plugins.env import MINUTES

from munin_plugins.utils.config import MuninConfiguration
from munin_plugins.utils.config import MuninSubConfiguration

class _PluginUtils(object):
  #converts a named tuple in dictionary (an inmmutable object to mutable object)
  def namedtuple2dict(self,nt,conv=lambda x: x):
    try:
      res=[conv((i,getattr(nt,i))) for i in nt._fields]
    except AttributeError:
      res=[]
    return dict(res)

  #converts 1024 in 1KiB
  def millify(self,value):
    byteunits = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')
    try:
      exponent = int(log(value, 1024))
      res="%.1f %s" % (float(value) / pow(1024, exponent), byteunits[exponent])
    except:
      res="0B"
    return res

  #convert a value in %
  def get_percent_of(self,val,full):
    try:
      percent = (val / full) * 100
    except ZeroDivisionError:
      # interval was too low
      percent = 0.0
    return percent

  #returns now - minutes
  def getlimit(self,minutes=MINUTES):
    return datetime.today()-timedelta(seconds=minutes*60)

class Plugin(MuninConfiguration,_PluginUtils):  
  _prefix_name='undefined'
  
  #Override of MuninConfiguration properties
  @property
  def _common(self):
    return {
      'user':'root',
      'group':'root',      
    }
  
  @property
  def _env(self):
    # Optional common entries:
    # 'cache':None, #cache file - option
    # 'enabled':None, #string composed by subplugins, see snsr_processes as example
    # 'sub_plugins_folder':None #folder of subplugins
    return {
      'title':'Undefined Title',#base title of plugin
      'group':'ungrouped', #munin group of plugin      
    }

  # Base plugin interface
  # Method to install/configure plugin in munin-node folder
  def install(self,plugins_dir,plug_config_dir,log,err):
    orig=join(sys.prefix,'bin',self._prefix_name)
    link=join(plugins_dir,self._prefix_name)
    
    def_create=not exists(link)    
    if def_create:
      def_label='Y/n'
    else:
      def_label='y/N'
    
    ans=raw_input("Install %s -> %s [%s]?"%(orig,link,def_label))    
    if (len(ans)==0 and def_create) or (len(ans)>0 and ans.lower()=='y'):        
      try:        
        symlink(orig,link)
        log("%s installed [%s,%s]"%(self._prefix_name.capitalize(),orig,link))
      except OSError:
        log("%s link NOT updated [%s,%s]"%(self._prefix_name.capitalize(),orig,link))

      config_file=join(plug_config_dir,self._prefix_name)

      #Storing main plugin config
      self.store(self._prefix_name,config_file)
      
      #Trying to store sub-plugins config
      try:          
        for name in self._env.get('enabled',None).split(','):
          try:
            sub=self.get_sub_plugin(self._env.get('sub_plugins_folder'),name)
          except (KeyError,ImportError,TypeError) as e:        
            pass
          else:
            sub().store(self._prefix_name,config_file)
      except AttributeError:
        #enabled is not set, means no subplugins  
        pass
            
      log("%s configured [%s]\n"%(self._prefix_name.capitalize(),config_file))
    
  # Method to run sensor, it should check if is config or not
  def main(self,argv=None, **kw):
    pass
    
  # Util methods
  def check_config(self,argv):
    if argv is None:
      argv = sys.argv[1:]
    return (len(argv)>0 and argv[0]=='config')
       
  def print_data(self,**args):
    id=args.get('id',None)
    v=args.get('value',None)
    if id is not None and v is not None:
      self.mkoutput(
        id=id,
        value=v)

  def print_config(self,**args):
    id=args.get('id',None)
    l=args.get('label',None)
    if id is not None and l is not None:
      self.mkoutput(
        id=id,
        label=l,
        draw=args.get('draw',None),
        type=args.get('type',None),
        warning=args.get('warning',None),
        critical=args.get('critical',None),
        colour=args.get('color',None),
        line=args.get('line',None),)

  def mkoutput(self,**argv):
    id=argv.get('id',None)
    if id is not None:
      del argv['id']
      for k,v in argv.items():
        if v is not None:
          row="%s.%s %s"
          if isinstance(v,float):              
            row="%s.%s %.3f"
          try:            
            print row%(id,k,v)
          except TypeError:
            print "%s.%s %s"%(id,k,v)


  #dynamic import of obj <name> from <lib>
  def get_sub_plugin(self,lib,name):    
    return getattr(__import__(lib,globals(),locals(),[name],-1),name)
  
class SubPlugin(MuninSubConfiguration,_PluginUtils):  
  @property
  def _env(self):
    # Optional common entries:
    # 'graph':'AREASTACK', #kind of subplugin
    # 'cache':None, #cache file
    return {
      'subtitle':'Undefined sub-Title',
      'label':'Undefined Label', 
    }


  
