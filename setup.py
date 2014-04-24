from setuptools import setup, find_packages

from os.path import join
from os.path import dirname
from os.path import abspath
from os import listdir

from munin_plugins.base_info import NAME
from munin_plugins.base_info import SYS_CONFIG_MUNIN_DIR
from munin_plugins.base_info import SYS_CONFIG_NGINX_DIR
from munin_plugins.base_info import SYS_CACHE_DIR
from munin_plugins.base_info import SYS_VAR_PATH
from munin_plugins.base_info import EGG_CONFIG_DIR
from munin_plugins.base_info import EGG_CONFIG_MUNIN_DIR
from munin_plugins.base_info import EGG_CONFIG_NGINX_DIR
from munin_plugins.base_info import EGG_CACHE_DIR

version = '4.1'

current=abspath(dirname(__file__))
  
config_base_dir=EGG_CONFIG_DIR
config_base_dir=join(current,NAME,config_base_dir)
config_base_files=[join(NAME,config_base_dir,f) for f in listdir(config_base_dir)]
  
config_munin_dir=EGG_CONFIG_MUNIN_DIR
config_munin_dir=join(current,NAME,config_munin_dir)
config_munin_files=[join(NAME,config_munin_dir,f) for f in listdir(config_munin_dir)]

config_nginx_dir=EGG_CONFIG_NGINX_DIR
config_nginx_path=join(current,NAME,config_nginx_dir)
config_nginx_files=[join(NAME,config_nginx_dir,f) for f in listdir(config_nginx_path)]

cache_dir=EGG_CACHE_DIR
cache_path=join(current,NAME,cache_dir)
cache_files=[join(NAME,cache_dir,f) for f in listdir(cache_path)]

setup(name=NAME,
      version=version,
      description="Sensors for munin",
      long_description=open(join(current,'README')).read(),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration', 
	    ],
      keywords='plone nginx monit munin sensors',
      author='Cippino',
      author_email='cippinofg <at> gmail <dot> com',
      url='https://github.com/cippino/munin_plugins',
      license='LICENSE.txt',
      packages=find_packages(),
      data_files = [(SYS_CONFIG_MUNIN_DIR,config_munin_files),
                    (SYS_CONFIG_NGINX_DIR,config_nginx_files),
                    (SYS_CACHE_DIR,cache_files),
                    (SYS_VAR_PATH,config_base_files)],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'psutil >= 2.0.0'
      ],
      entry_points={
        "console_scripts":[
          "generate = munin_plugins.generate:main",
          "monit_downtime = munin_plugins.monit_downtime:main",
          "nginx_full = munin_plugins.nginx_full:main",
          "plone_usage = munin_plugins.plone_usage:main",
        ]
      },
)
        

