#source /home/ubuntu/.bashrc

export LD_LIBRARY_PATH=/usr/local/cuda-6.5/lib:/usr/local/lib:/usr/lib:/lib:
#. /home/ubuntu/.bashrc
cd /home/ubuntu/2016-Vision/VideoStream

nohup python webCameraTest.py

