#!/bin/bash

rm -fr /opt/munin/
rm -fr build dist

virtualenv /opt/munin

/opt/munin/bin/python setup.py bdist_egg

/opt/munin/bin/easy_install dist/munin_plugins-5.0-py2.7.egg

/opt/munin/bin/generate


#./test_bot_call.sh
#./test.sh
#/etc/init.d/munin-node restart
