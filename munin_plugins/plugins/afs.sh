#!/bin/bash
if [ "$1" = "config" ]; then
  echo "graph_title AFS Latency"
  echo "graph_args -l 0 --base 1000"
  echo "graph_vlabel AFS Latency for an LS"
  echo "graph_category network"
  echo "ls.label ls /afs/enea.it/user/g/guizzard/"
  echo "ls1.label ls /afs/enea.it/project/campus/webtv/"
  echo "ls.min 0"
  echo "ls1.min 0"
else 
  export TIMEFORMAT="%E"
  val=`time (timeout 2m ls /afs/enea.it/user/g/guizzard/) 2>&1 >/dev/null`
  echo "ls.value $val"
  val=`time (timeout 2m ls /afs/enea.it/project/campus/webtv/) 2>&1 >/dev/null`
  echo "ls1.value $val"
fi

