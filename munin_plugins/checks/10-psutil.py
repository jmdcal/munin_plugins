def check(log,err):
  try: 
    import psutil
    log("Psutil is ok [%s.%s.%s]"%psutil.version_info)
  except ImportError:
    err("Unable import psutil")
