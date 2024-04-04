#!/bin/bash

SERVICE='nginx'
STATUS=$(ps ax | grep -v grep | grep $SERVICE)

if [ "$STATUS" != "" ]
then
    exit 0
else
    exit 1
fi
