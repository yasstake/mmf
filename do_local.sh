#!/bin/bash



gcloud ml-engine local train \
    --package-path ./dl   \
    --module-name dl.train

#    --python-version 3.5 \
#    --runtime-version 1.12 \
#    --region us-central1
