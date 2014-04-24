from os.path import join
from sys import prefix

NAME='munin_plugins'
EGG_CONFIG_DIR='config'
EGG_CONFIG_MUNIN_DIR='config_munin'
EGG_CONFIG_NGINX_DIR='config_nginx'
EGG_CACHE_DIR='cache'

SYS_VAR_PATH=join(prefix,'var',NAME)
SYS_CONFIG_MUNIN_DIR=join(SYS_VAR_PATH,EGG_CONFIG_MUNIN_DIR)
SYS_CONFIG_NGINX_DIR=join(SYS_VAR_PATH,EGG_CONFIG_NGINX_DIR)
SYS_CACHE_DIR=join(SYS_VAR_PATH,EGG_CACHE_DIR)

