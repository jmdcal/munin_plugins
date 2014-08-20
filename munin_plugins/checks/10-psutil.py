"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'

def check(log,err):
  try: 
    import psutil
    log("Psutil is ok [%s.%s.%s]"%psutil.version_info)
  except ImportError:
    err("Unable import psutil")
