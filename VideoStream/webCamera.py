from time import time
from flask import Flask, render_template, Response
import numpy as np
import cv2
import os
import time
from cv2 import *
import sys
import socket
import select
import math
from flask import request


xError = 24
yError = 24
xTarget = 320
yTarget = 200 


port = 5801
host = 'roboRIO-4499-FRC.local'

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

cap_two = cv2.VideoCapture(1)
cap_two.set(3,640)
cap_two.set(4,480)

errorFrameOne = open('/home/ubuntu/VideoStream/templates/PolarBearError.jpg','rb').read()

app = Flask(__name__)

class Camera(object):
    """An emulated camera implementation that streams a repeated sequence of
    files 1.jpg, 2.jpg and 3.jpg at a rate of one frame per second."""

    def __init__(self):
	print "Init Camera"
        self.frames = [open(f + '.jpg', 'rb').read() for f in ['1', '2', '3']]

    def get_frame(self):
	print "requested Frame"
        return self.frames[int(time()) % 3]


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def vision(cap):
	ret, frame = cap.read()

	# show the original frame (Testing only)	
	#cv2.imshow('Original',frame)

	#do conversions for the mask
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	lower_green = np.array([30, 46, 108]) #These values can be found with calibration tool
	upper_green = np.array([89, 125, 255])

	# Threshold the HSV image to get only green colors
	mask = cv2.inRange(hsv, lower_green, upper_green)

	#Show the mask (Testing Only)
	#cv2.imshow('mask',mask)


	#Find the contours of the masked image
	ret,thresh = cv2.threshold(mask,200,255,0)
	contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)


	#Make sure that a contour region is found
	if len(contours) > 1:
		#find Biggest Contour region
		areas = [cv2.contourArea(c) for c in contours]
		max_index = np.argmax(areas)
		cnt=contours[max_index]
	
		#Find the smallest bounding box of the rectangle
		rect = cv2.minAreaRect(cnt)
		box = cv2.cv.BoxPoints(rect)
		box = np.int0(box)
		
		#find center of target for RoboRIO
		xCenter = (box[0][0] + box[1][0] + box[2][0] + box[3][0]) / 4
		yCenter = (box[0][1] + box[1][1] + box[2][1] + box[3][1]) / 4
		
		#These Calculations and draw settings are to help the driver lock onto the target
		xLocked = abs(xTarget - xCenter) < xError
		yLocked = abs(yTarget - yCenter) < yError
		if(xLocked):
			cv2.line(frame,(320,0),(320,480),(0,0,255),3)
		else:
			cv2.line(frame,(320,0),(320,480),(255,0,0),3)
		if(yLocked):
			cv2.line(frame,(0,yCenter),(640,yCenter),(0,0,255),3)
		else:				
			cv2.line(frame,(0,yCenter),(640,yCenter),(255,0,0),3)
		if(xLocked and yLocked):
			cv2.drawContours(frame,[box],0,(0,0,255),2)
		else:
			cv2.drawContours(frame,[box],0,(0,255,0),2)
		msg = '(' + str(xCenter) + ',' + str(yCenter) + ')\n'
	else:
		msg = '( 0,0)\n'

	#show final image (Testing only)		
#	cv2.imshow("Show",frame)
	#Quit if q is pressed
   	if cv2.waitKey(1) & 0xFF == ord('q'):
		print exitKey
	return msg , frame
	


def gen(camera, value):
    """Video streaming generator function."""
    count = 0
    lastTime = 0
    
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.settimeout(2)
     
    # connect to remote host
    try :
        soc.connect((host, port))
	print 'found target'
	soc.send("#Found you\n")
    except :
        print 'Unable to connect'
        sys.exit()


    while 1:
	#frame = camera.get_frame()
	millis = int(round(time.time()*1000))
	if(value == 0):
		msg, CVframe = vision(cap)
		try:
			soc.send(msg)
		except :
       			print 'Lost Connection with Roborio'
			soc.connect((host, port))
			print('found target')
			soc.send("#Found you\n")
			
		#cv2.imwrite("frame%d.jpg" % count, CVframe)
		#frame = open("frame%d.jpg" % count,'rb').read()
		frame = cv2.imencode('.jpg',CVframe,[IMWRITE_JPEG_QUALITY, 10])[1].tostring()
	
	else:
	
		ret, CVframe = cap_two.read()
		if(ret == True):
			frame = cv2.imencode('.jpg',CVframe,[IMWRITE_JPEG_QUALITY, 10])[1].tostring()
		else:
			frame = errorFrameOne
		
	#print(millis-lastTime)

	yield (b'--frame\r\n'
	       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
	#os.remove("frame%d.jpg" % count)	
	count = count + 1
#	break
	if cv2.waitKey(1) & 0xFF == ord('q'):
		#os.remove("/home/void/Documents/frames/frame%d.jpg" % count)
		
        	break
	lastTime = int(round(time.time()*1000))

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(),0),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_two')
def video_feed_two():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(),1),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5800, threaded=True)

cap.release()
cap_two.release()
cv2.destroyAllWindows()
print("Ended Feed")

