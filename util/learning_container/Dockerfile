FROM nvcr.io/nvidia/tensorflow:19.03-py3

RUN apt-get update -y
RUN apt-get install -y git gzip curl wget python lsb-release gnupg apt-utils
RUN apt-get install cmake libopenmpi-dev python3-dev zlib1g-dev

RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update -y && apt-get install google-cloud-sdk -y

RUN cd /tmp; wget https://bootstrap.pypa.io/get-pip.py && /usr/bin/python3 get-pip.py

RUN python3 -m pip install websocket-client==0.47

RUN python3 -m pip install --upgrade google-cloud-storage
RUN python3 -m pip install gym
RUN python3 -m pip install numpy
RUN python3 -m pip install matplotlib
RUN python3 -m pip install --upgrade sklearn
RUN python3 -m pip install stable-baselines



CMD cd /home/yass/Projects/mmf && python3 -m agent.apex > /bitlog/learn.log












