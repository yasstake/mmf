FROM ubuntu

RUN apt-get update -y
RUN apt-get install -y git gzip curl wget python lsb-release gnupg apt-utils

RUN apt-get install -y python3.7 python3-distutils

RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" && \
    echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update -y && apt-get install google-cloud-sdk -y

RUN cd /tmp && wget https://bootstrap.pypa.io/get-pip.py && /usr/bin/python3.7 get-pip.py

RUN /usr/bin/python3.7 -m pip install websocket-client==0.47
RUN /usr/bin/python3.7 -m pip install

RUN echo ""

RUN git clone https://github.com/yasstake/mmf.git

ADD ./net2log.sh /mmf/net2log.sh
RUN chmod a+x /mmf/net2log.sh
CMD /mmf/net2log.sh





