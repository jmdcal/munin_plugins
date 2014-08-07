from os.path import join
from sys import prefix
from munin_plugins.base_info import NAME

SYS_VAR_PATH=join(prefix,'var',NAME)

CACHE=join(SYS_VAR_PATH,'cache')

MINUTES=5

