#!/usr/bin/env bash

sudo apt-get update -y
sudo apt-get install -y git gzip curl wget python lsb-release gnupg apt-utils
sudo apt-get install -y python3 python3-distutils
sudo apt-get install -y docker.io
sudo apt-get install -y curl wget
export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
        curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add - && \
        sudo apt-get update -y && sudo apt-get install google-cloud-sdk -y
cd /tmp; wget https://bootstrap.pypa.io/get-pip.py && sudo /usr/bin/python3.7 get-pip.py

sudo python3 -m pip install websocket-client==0.47

sudo python3 -m pip install --upgrade google-cloud-storage
sudo python3 -m pip install gym
sudo python3 -m pip install numpy
sudo python3 -m pip install matplotlib
sudo python3 -m pip install --upgrade sklearn

