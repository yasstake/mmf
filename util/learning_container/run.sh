
nohup sudo docker run -v /bitlog:/bitlog -v /home/yass:/home/yass -u $(id -u):$(id -g) --memory 50g --oom-kill-disable --runtime=nvidia -d dl > /bitlog/learn.log


