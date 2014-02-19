from setuptools import setup, find_packages
import sys, os

version = '4.0.1'

name='munin_plugins'

current=os.path.abspath(os.path.dirname(__file__))
  
config_dir='config'
config_path=os.path.join(current,name,config_dir)
config_files=[os.path.join(name,config_dir,f) for f in os.listdir(config_path)]

config_ext_dir='config_ext'
config_ext_path=os.path.join(current,name,config_ext_dir)
config_ext_files=[os.path.join(name,config_ext_dir,f) for f in os.listdir(config_ext_path)]

cache_dir='cache'
cache_path=os.path.join(current,name,cache_dir)
cache_files=[os.path.join(name,cache_dir,f) for f in os.listdir(cache_path)]

setup(name=name,
      version=version,
      description="Sensors for munin",
      long_description=open('README').read(),
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
      data_files = [(os.path.join(sys.prefix,'var',name,config_dir) ,config_files),
                    (os.path.join(sys.prefix,'var',name,config_ext_dir) ,config_ext_files),
                    (os.path.join(sys.prefix,'var',name,cache_dir) ,cache_files),],
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
        

