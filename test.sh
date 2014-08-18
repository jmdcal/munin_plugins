#!/bin/bash 


for sns in snsr_apache snsr_monit snsr_nginx snsr_processes snsr_repmgr; do 
  echo -n "--> $sns.."
  munin-run $sns > /dev/null
  if [ "$?" == "0" ]; then
   echo ".ok"
  else
    echo ".fail"    
  fi
  echo -n "--> $sns config.."
  munin-run $sns config > /dev/null
  if [ "$?" == "0" ]; then 
   echo ".ok"
  else
    echo ".fail"    
  fi

done

# munin-run snsr_apache
# munin-run snsr_apache config
# munin-run snsr_apache
# munin-run snsr_apache config