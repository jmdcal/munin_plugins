from munin_plugins.utils.caches import CacheDict
from munin_plugins.utils.caches import CacheCounter
from munin_plugins.utils.caches import CachePickle

from munin_plugins.utils.parsers import ApacheRowParser
from munin_plugins.utils.parsers import NginxRowParser

def mkoutput(**argv):
  id=argv.get('id',None)
  if id is not None:
    del argv['id']
    for k,v in argv.items():
      if v is not None:
        try:
          print "%s.%s %.3f"%(id,k,v)
        except TypeError:
          print "%s.%s %s"%(id,k,v)

def print_data(**args):
  id=args.get('id',None)
  v=args.get('value',None)
  if id is not None and v is not None:
    mkoutput(id=id,
             value=v)

def print_config(**args):
  id=args.get('id',None)
  l=args.get('label',None)
  if id is not None and l is not None:
    mkoutput(id=id,
             label=l,
             draw=args.get('draw',None),
             type=args.get('type',None),
             warning=args.get('warning',None),
             critical=args.get('critical',None),
             colour=args.get('color',None),
             line=args.get('line',None),)
