import sys
import re

from os.path import join
from os.path import exists
from os import environ
from os import symlink

from datetime import datetime
from datetime import timedelta

from munin_plugins.env import MINUTES

class Plugin(object):  
  _title='Undefined'
  _group='Undefined'
  _defaults={}  
  _prefix_env='undefined'
  _prefix_name='undefined'
    
  def check_config(self,argv):
    argv=self.fixargs(argv)
    return (len(argv)>0 and argv[0]=='config')
  
  def getenv(self,id,null=None):
    val=environ.get(id,self._defaults.get(id,null))
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
  
  def getenvs(self,pref):
    return [e.split(',') for i,e in environ.items() if re.match('^%s'%pref,i)]  

  def getenvs_with_id(self,pref):
    return [[i.replace(pref,'')]+e.split(',') for i,e in environ.items() if re.match('^%s'%pref,i)]  

  
  def paths(self,plugins_dir):
    return (join(sys.prefix,'bin',self._prefix_name),join(plugins_dir,self._prefix_name))
  
  def ask(self,plugins_dir):
    orig,link=self.paths(plugins_dir)
    def_create=not exists(link)
    
    if def_create:
      def_label='Y/n'
    else:
      def_label='y/N'
    
    return (raw_input("Link %s -> %s [%s]?"%(orig,link,def_label)),def_create)
  
  
  def install_plugin(self,plugins_dir,plug_config_dir,extended={},env={}):
    orig,link=self.paths(plugins_dir)
    try:        
      symlink(orig,link)
      print "%s installed [%s,%s]\n"%(self._prefix_name.capitalize(),orig,link)
    except OSError:
      print "%s NOT updated [%s,%s]\n"%(self._prefix_name.capitalize(),orig,link)

    config_file=join(plug_config_dir,self._prefix_name)
      
    with open(config_file,'w') as fd:
      fd.write('[%s]\n'%self._prefix_name)
      fd.write('user root\n')
      fd.write('group root\n')
      if extended is not None:
        for k,v in extended.items():
           fd.write('%s %s\n'%(k,v))
      if env is not None:
        for k,v in env.items():
           fd.write('env.%s %s\n'%(k,v))
          
    print "%s configured [%s]"%(self._prefix_name.capitalize(),config_file)

  
  def print_config(self,title,group,vals):
    pass

  def install(self,plugins_dir,plug_config_dir):
    pass

  def main(self,argv=None, **kw):
    pass
  
  
 
  def fixargs(self,argv):
    if argv is None:
      argv = sys.argv[1:]
    return argv



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
          try:
            print "%s.%s %.3f"%(id,k,v)
          except TypeError:
            print "%s.%s %s"%(id,k,v)

  def getlimit(self,minutes=MINUTES):
    actual_time=datetime.today()
    delay=timedelta(seconds=minutes*60)
    return actual_time-delay

  def namedtuple2dict(self,nt,conv=lambda x: x):
    return dict(self.namedtuple2list(nt,conv))
  
  def namedtuple2list(self,nt,conv=lambda x: x):
    try:
      res=[conv((i,getattr(nt,i))) for i in nt._fields]
    except AttributeError:
      res=[]
    return res
  