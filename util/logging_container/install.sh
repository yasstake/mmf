#!/usr/bin/env bash

sudo apt-get update -y
sudo apt-get install -y git gzip curl wget python lsb-release gnupg apt-utils
sudo apt-get install -y python3.7 python3-distutils
sudo export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
        curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
        apt-get update -y && apt-get install google-cloud-sdk -y
sudo cd /tmpt https://bootstrap.pypa.io/get-pip.py && /usr/bin/python3.7 get-pip.py
sudo /usr/bin/python3.7 -m pip install websocket-client==0.47
sudo /usr/bin/python3.7 -m pip install --upgrade google-cloud-storage
