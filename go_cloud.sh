#!/bin/bash


JOBNAME=mmfjob08

#gcloud ml-engine local train  \
gcloud ml-engine jobs submit training ${JOBNAME} \
    --job-dir gs://mlpackage/mmfjob \
    --package-path ./dl   \
    --python-version 3.5 \
    --module-name dl.train \
    --runtime-version 1.13 \
    --region us-central1

gcloud ml-engine jobs stream-logs ${JOBNAME}