"""

This file is a part of Munin_Plugin project.
You can find any information you like at urls

https://pypi.python.org/pypi/munin_plugins
https://github.com/cippino/munin_plugins

"""

__author__ = 'Federico C. Guizzardi cippinofg_at_gmail_com'
__copyright__ = 'Copyright 2014, Federico C. Guizzardi'
__license__ = 'GPL Version 2.0'

from os import makedirs
from os.path import exists
from os.path import join

from munin_plugins.env import CACHE

def check(log,err):  
  if not exists(CACHE):
    makedirs(CACHE) 
    log("Cache is ok (created) [%s]"%CACHE)
  else:
    log("Cache is ok [%s]"%CACHE)
