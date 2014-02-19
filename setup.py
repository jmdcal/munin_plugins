from setuptools import setup, find_packages

from os.path import join
from os.path import dirname
from os.path import abspath
from os import listdir


from munin_plugins.etc.env import NAME
from munin_plugins.etc.env import SYS_CONFIG_DIR
from munin_plugins.etc.env import SYS_CONFIG_EXT_DIR
from munin_plugins.etc.env import SYS_CACHE_DIR
from munin_plugins.etc.env import EGG_CONFIG_DIR
from munin_plugins.etc.env import EGG_CONFIG_EXT_DIR
from munin_plugins.etc.env import EGG_CACHE_DIR

version = '4.0.1'

current=abspath(dirname(__file__))
  
config_dir=EGG_CONFIG_DIR
config_path=join(current,NAME,config_dir)
config_files=[join(NAME,config_dir,f) for f in listdir(config_path)]

config_ext_dir=EGG_CONFIG_EXT_DIR
config_ext_path=join(current,NAME,config_ext_dir)
config_ext_files=[join(NAME,config_ext_dir,f) for f in listdir(config_ext_path)]

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
      data_files = [(SYS_CONFIG_DIR,config_files),
                    (SYS_CONFIG_EXT_DIR,config_ext_files),
                    (SYS_CACHE_DIR,cache_files),],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'psutil >= 1.0.1'
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
        

