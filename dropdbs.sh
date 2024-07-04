#!/bin/bash

# Script to drop mulitple dbs at one go, 
# usage : sh dropdbs.sh  db1 db2 db3


# Iterate through each argument passed to the script
for dbname in "$@"; do
    # Attempt to drop the database
    echo "Dropping database $dbname..."
    dropdb "$dbname"
    
    # Check if the dropdb command was successful
    if [ $? -eq 0 ]; then
        echo "Database $dbname dropped successfully"
    else
        echo "Failed to drop database $dbname"
    fi
done
