#!/usr/bin/env bash

set -e

: "${1:?"Incorrect usage: `basename $0` NAMESPACE"}"

root=`cd $(dirname $0); cd ..; pwd`
secret=monitor-secrets
ns=$1

function get_secret {
    value=`kubectl get secret $secret --namespace $ns --template "{{ .data.$1 }}"`

    if [ `uname` == "Darwin" ]; then
        echo `echo $value | base64 -D`
    else
        echo `echo $value | base64 -d`
    fi
}

# VAL=$(base64decode `kubectl get secret $secrets --namespace $1 --template '{{ .data.dburi }}'`)
export A01_DATABASE_URI=$(get_secret dburi)
export AZURE_CLIENT_ID=$(get_secret client_id)
export AZURE_CLIENT_TENANT=$(get_secret client_tenant)
export AZURE_CLIENT_SECRET=$(get_secret client_secret)
export AZURE_CLIENT_RESOURCE=$(get_secret client_resource)

export FLASK_APP=$root/app/app/main.py
export FLASK_DEBUG=1

pipenv run flask run
