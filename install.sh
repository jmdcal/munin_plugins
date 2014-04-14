#!/bin/bash

rm -fr /opt/munin/lib/python2.7/site-packages/munin_plugins-4.0.2-py2.7.egg
/opt/munin/bin/python setup.py build
/opt/munin/bin/python setup.py install