#!/bin/bash


sudo apt-get update
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

sudo apt-get update
sudo apt-get install -y --allow-downgrades docker-ce=5:18.09.0~3-0~ubuntu-bionic
#sudo apt-get install docker-ee=5:18.09.5~3-0~ubuntu-bionic

