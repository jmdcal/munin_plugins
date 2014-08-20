try:
  from setuptools import setup, find_packages
except:
  from ez_setup import use_setuptools
  use_setuptools()  

from os.path import join
from os.path import dirname
from os.path import abspath

from munin_plugins.base_info import NAME

version = '5.0'

current=abspath(dirname(__file__))

setup(name=NAME,
      version=version,
      description="Sensors for munin",
      long_description=open(join(current,'README.rst')).read(),
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
      package_data={'': ['config*/*','cache/*']},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'psutil >= 2.0.0'
      ],
      entry_points={
        "console_scripts":[
          "generate = munin_plugins.generate:main",
          "snsr_apache = munin_plugins.plugins.snsr_apache:main",
          "snsr_monit = munin_plugins.plugins.snsr_monit:main",
          "snsr_nginx = munin_plugins.plugins.snsr_nginx:main",
          "snsr_processes = munin_plugins.plugins.snsr_processes:main",
          "snsr_repmgr = munin_plugins.plugins.snsr_repmgr:main",
        ]
      },
)
        

