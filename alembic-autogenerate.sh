#!/bin/bash 

if [[ -z $1 ]]; then 
	echo "You need provide the comment for the migration"
	exit -1
else 
	alembic revision --autogenerate -m "$1"
fi 

