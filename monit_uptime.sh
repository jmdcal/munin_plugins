#!/bin/bash


if [ "$1" = "config" ]; then
    echo 'graph_title Monit Uptime'
    echo 'graph_args --base 1000 -l 0 '
    echo 'graph_scale no'
    echo 'graph_vlabel uptime in days'
    echo 'graph_category monitor'
    echo 'uptime.label uptime'
    echo 'uptime.draw AREA'
   
    exit 0
fi

upt=`monit summary |grep uptime | cut -d' ' -f6`
if [[ "upt" = *d ]]; then
  val=`echo $upt |sed -e s/d//`
else
  val=0
fi
echo "uptime.value $val"