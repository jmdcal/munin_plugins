=====
Intro
=====

This is a suite of sensors (plugins) for munin. You can install one or all, as 
you wish.

Sensors available for:

* Apache
* Monit
* Nginx
* Processes (Plone, Zope, JBoss actually)
* Repmgr

============
Requirements
============

* Python >= 2.7
* psutil for Python >= 2.0
* Munin-node

=======
Install
=======

Install Egg
-----------

As usual, egg is installable using setuptools or pip, choice what you like. 
It is better and strongly suggested to use a virtualenv.
    
Setup plugins
-------------

The fast way to install, is using generate.py. To use, simply call generate script
in bin directory.

:: 

    $ <virtualenv_path>/bin/generate
  

It will test the environment and configure cache folders. For every sensor, it will
ask a confirm. Every sensor creates in /etc/munin/plugin-conf.d a single configuration.
If you want to check/change, that is the place.  
        
Restart munin-node, munin-async (if you use that) and enjoy.

More details at

http://cippino.wordpress.com/tag/munin/
https://github.com/cippino/munin_plugins
https://pypi.python.org/pypi/munin_plugins

Configure Nginx or Apache 
-------------------------

Usually a manual configuration is not required, but in some case you have to modify 
some path or else. All munin plugins ask by they self during installation what 
they need, and they write in /etc/munin/plugin-conf.d. Keep attention if you reinstall
using generate script because all setup will be overwriten.

For apache and nginx, you have to configure log file format using combined2:

::

    Apache: LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" [[%D]]" combined2

::

    Nginx: log_format combined2 '$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent "$http_referer" "$http_user_agent" [[$request_time]]';

After combined2 definition, you have to change your virtualhost configuration using 
this format instead of usual "combined".

Customize Setup
---------------

Every pluging you installed with "generate" script writes in /etc/munin/plugin-conf.d 
a specific config file. You can modify every option you find. It shouldn't require
munin-node reload.

=======
Warning
=======

Previous version of 4.3 are not complatible with 4.3 and later release, because 
some sensors are renamed/moved/merged, so apply an upgrade will lose all history
informations.

================================
Bugs Report and/or Collaboration
================================

GitHub is the current store for sources:

https://github.com/cippino/munin_plugins

Any idea is welcome.


=========
Changelog
=========

- 5.0 
    * Refactor to move all configurations in /etc/munin/plugin-conf.d files

- 4.3
    * Merged plone_usage and java in processes_usage

- 4.2: 
    * Refactor setup and sensor using classes

- 4.1.3
    * Fixed VAR folder creation

- 4.1.2
    * Fixed Egg Configure Folders

- 4.1.1
    * Fixed Documentation

- 4.1 
    * Refactor of env.py and configuration
    * Refactor of plone_usage from monolithic implementation to modular
    * Reduced number of Cache classes

- 4.0
    * First Egg release

==============
Known Problems
==============

1 - Keep attection if you use SELinux or other kind of Security access framework,
because you have to configure all rights correctly. Usually, my choice is to
put down, because the call of monit get error about access denied.



