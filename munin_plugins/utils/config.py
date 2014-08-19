import re

from os import environ
from os.path import exists

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
    val=environ.get(k,self._env.get(k,alt))
    try:
      #trying to parse int, boolean
      val=eval(val.capitalize())
    except NameError: #means no object found
      pass
    except SyntaxError: #means parser get a syntax error      
      pass
    except AttributeError: #means capitalize is not valid
      pass    
    return val

  def getenv_prefix(self,pref,alt=None):
    #getting from static class config
    res=dict([(k,v.split(',')) for k,v in self._env.items() if re.match('^%s'%pref,k)])
    
    #ovveride values from environ
    for k,v in environ.items():
      if re.match('^%s'%pref,k):
        res[k]=v.split(',')
    
    return res.values()

  def getenv_prefix_with_id(self,pref):
    #getting from static class config
    res=dict([(k,[k.replace(pref,'')]+v.split(',')) for k,v in self._env.items() if re.match('^%s'%pref,k)])

    #ovveride values from environ
    for k,v in environ.items():
      if re.match('^%s'%pref,k):
        res[k]=[k.replace(pref,'')]+v.split(',')
    
    return res.values()
      
class MuninSubConfiguration(MuninConfiguration):      
  def getsubid(self,id):
    try:
      sub_id='%s_%s'%(self.__class__.__name__,id)
    except AttributeError:
      sub_id=id      
    return sub_id
  
  def getenv(self,k,alt=None):    
    val=environ.get(self.getsubid(k),self._env.get(k,super(MuninSubConfiguration,self).getenv(k,alt)))
    try:
      #trying to parse int, boolean
      val=eval(val.capitalize())
    except NameError: #means no object found
      pass
    except SyntaxError: #means parser get a syntax error      
      pass
    except AttributeError: #means capitalize is not valid
      pass    
    return val

  def getenv_prefix(self,prefix,alt=None):    
    #getting from static class config
    res=dict([(k,v.split(',')) for k,v in self._env.items() if re.match('^%s'%pref,k)])
    
    prefix=self.getsubid(prefix)
    #ovveride values from environ
    for k,v in environ.items():
      if re.match('^%s'%pref,k):
        res[k]=v.split(',')
    
    return res

  def getenv_prefix_with_id(self,pref):
    #getting from static class config
    res=dict([(k,[k.replace(pref,'')]+v.split(',')) for k,v in self._env.items() if re.match('^%s'%pref,k)])

    prefix=self.getsubid(prefix)
    #ovveride values from environ
    for k,v in environ.items():
      if re.match('^%s'%pref,k):
        res[k]=[k.replace(pref,'')]+v.split(',')
    
    return res
    
  def store(self,section,filename):
    with open(filename,'a') as fd:
      fd.write('#Written by %s\n'%self.__class__.__name__)
      for k,v in self._common.items():
        fd.write('%s %s\n'%(k,v))
      
      for k,v in self._env.items():
        fd.write('env.%s %s\n'%(self.getsubid(k),v))
      fd.write('#End written by %s\n\n'%self.__class__.__name__)

