#!/bin/bash

if [ "$1" == "sandbox" ]; then
    open -a "Google Chrome" "http://localhost:8000/api/qbo/connect/sandbox?company_id=1"
elif [ "$1" == "production" ]; then
    open -a "Google Chrome" "http://localhost:8000/api/qbo/connect/production?company_id=1"
else
    echo "Usage: $0 {sandbox|production}"
fi