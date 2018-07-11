#!/usr/bin/bash
set -e
remote_file=$1

if [ $# -gt 1 ]
then
    local_file=$2
    file_name=$local_file
else
    local_file="."
    file_name=$(basename $1)
fi

timeout=60

num_changes=2
i=0

if [ -f $file_name ]
then
    read old_checksum rest < <(cksum $file_name)
else
    old_checksum=""
fi

while [ $num_changes -gt 0 ]
do
    if [ $i -gt 0 ]
    then
        echo "Sleeping."
        sleep $timeout
    fi

    rsync -azP $remote_file $local_file
    read new_checksum rest < <(cksum $file_name)

    if [ "$old_checksum" = "$new_checksum" ]
    then
       num_changes=0
    fi

    old_checksum=$new_checksum

    i=$(($i+1))
done
