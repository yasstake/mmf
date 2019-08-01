
sudo docker run -v /bitlog:/bitlog -v /home/yass:/home/yass -u $(id -u):$(id -g) --runtime=nvidia -d dl

