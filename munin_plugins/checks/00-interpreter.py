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

def check(log,err):
  vers=sys.version_info
  if vers<(2,7):
    err("Python version is not valid (required 2.7.x)")
  else:
    log("Python is ok [%s.%s.%s %s-%s]"%(vers.major,vers.minor,vers.micro,vers.releaselevel,vers.serial))
  
