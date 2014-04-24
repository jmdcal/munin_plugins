#!/bin/bash

rm -fr /opt/munin/lib/python2.7/site-packages/munin_plugins-*
rm -fr build dist
/opt/munin/bin/python setup.py build
/opt/munin/bin/python setup.py install
