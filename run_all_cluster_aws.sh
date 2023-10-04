#!/bin/bash

bash gen_conf_cluster_aws.sh
sleep 10

# Number of configuration files (experiments)
for i in {0..23}
do
  # Repetition of each experiment
  for j in {0..9}
  do
     echo "$i" "$j"
     bash start_cluster_aws.sh "$i"
     sleep 10
     pkill python3
  done
done
