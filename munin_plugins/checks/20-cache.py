from os import makedirs
from os.path import exists
from os.path import join

from ..env import SYS_VAR_PATH

def check(log,err):  
  dest=join(SYS_VAR_PATH,'cache')
  if not exists(dest):
    makedirs(dest) 
    log("Cache is ok (created) [%s]"%dest)
  else:
    log("Cache is ok [%s]"%dest)
