import sys 

def check(log,err):
  vers=sys.version_info
  if vers<(2,7):
    err("Python version is not valid (required 2.7.x)")
  else:
    log("Python is ok [%s.%s.%s %s-%s]"%(vers.major,vers.minor,vers.micro,vers.releaselevel,vers.serial))
  
