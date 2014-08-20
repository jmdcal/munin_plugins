"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'

import re

from os import environ

class MuninConfiguration(object):
  #Common options 
  _common={}
  
  #Environment variables
  _env={}
  
  def set_common(self,k,v):
    self._common[k]=v
    
  def set_env(self,k,v):
    self._env[k]=v

  def update_common(self,upd):
    if isinstance(upd,dict):
      self._common.update(upd)

  def update_env(self,upd):
    if isinstance(upd,dict):
      self._env.update(upd)
    
  def store(self,section,filename):
    with open(filename,'w') as fd:      
      fd.write('#Written by %s\n'%self.__class__.__name__)
      fd.write('[%s]\n'%section)

      for k,v in self._common.items():
        fd.write('%s %s\n'%(k,v))
      
      for k,v in self._env.items():
        fd.write('env.%s %s\n'%(k,v))
                  
      fd.write('#End written by %s \n\n'%self.__class__.__name__)
      
  def getenv(self,k,alt=None):    
    val=environ.get(k,alt)
    try:
      #trying to parse int, boolean
      val=eval(val.capitalize())
    except (NameError,SyntaxError,AttributeError): #means (no object found,parser get a syntax error,capitalize is not valid)
      #val is a simple text
      pass
    return val

  def getenv_prefix(self,prefix):
    return [v.split(',') for k,v in environ.items() if re.match('^%s'%prefix,k)]
    
  def getenv_prefix_with_id(self,prefix):
    return [[k.replace(prefix,'')]+v.split(',') for k,v in environ.items() if re.match('^%s'%prefix,k)]
      
class MuninSubConfiguration(MuninConfiguration):      
  def getsubid(self,id):
    try:
      sub_id='%s_%s'%(self.__class__.__name__,id)
    except AttributeError:
      sub_id=id      
    return sub_id
  
  def getenv(self,k,alt=None):    
    mtd=super(MuninSubConfiguration,self).getenv
    return mtd(self.getsubid(k),mtd(k,alt))

  def getenv_prefix(self,prefix,alt=None):        
    return super(MuninSubConfiguration,self).getenv_prefix(self.getsubid(prefix),alt)

  def getenv_prefix_with_id(self,prefix):
    return super(MuninSubConfiguration,self).getenv_prefix_with_id(self.getsubid(prefix),alt)
    
  def store(self,section,filename):
    with open(filename,'a') as fd:
      fd.write('#Written by %s\n'%self.__class__.__name__)
      for k,v in self._common.items():
        fd.write('%s %s\n'%(k,v))
      
      for k,v in self._env.items():
        fd.write('env.%s %s\n'%(self.getsubid(k),v))
      fd.write('#End written by %s\n\n'%self.__class__.__name__)

