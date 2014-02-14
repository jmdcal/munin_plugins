from setuptools import setup, find_packages
import sys, os

version = '4.0.0'

setup(name='munin_plugins',
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
