#!/bin/bash

#running=$(qstat -u ${USER} | egrep "bench_sequential.*[R|Q]")
#if [ -n "${running}" ] ;
#then
#    echo "------------------------------------"
#    echo ${USER} has this job in the queue or running 
#    qstat | grep ${USER}
#    echo
#    echo please delete this job or wait for it to complete
#    exit 1
#fi

sbatch --partition=Centaurus --chdir=`pwd` --time=02:00:00 --ntasks=1 --cpus-per-task=1 --mem=40G --job-name=mod4mss bench_sequential.sh
