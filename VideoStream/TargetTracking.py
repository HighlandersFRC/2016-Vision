from time import time
from flask import Flask, render_template, Response, request, jsonify, send_from_directory
import numpy as np
import cv2
import glob, os
import time
from cv2 import *
import sys
import socket
import select
import math
from flask import request

port = 5801
host = '10.44.99.2'

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

cap_two = cv2.VideoCapture(1)
cap_two.set(3,640)
cap_two.set(4,480)


cap_three = cv2.VideoCapture(2)
cap_three.set(3,640)
cap_three.set(4,480)

app = Flask(__name__, static_url_path='')

global h_div
global s_div
global v_div
global xTarget
global yTarget
global save_name
global save_now

h_div = 16
s_div = 19
v_div = 19
save_name = ""
save_now = 0

xError = 24
yError = 24
xTarget = 320
yTarget = 240 


pandaBearError = open("/home/ubuntu/2016-Vision/VideoStream/templates/PandaBearError.jpg",'rb').read()
polarBearError = open("/home/ubuntu/2016-Vision/VideoStream/templates/PolarBearError.jpg",'rb').read()

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def vision(cap):
	ret, frame = cap.read()

	global h_div
	global s_div
	global v_div
	global xTarget
	global yTarget
	# show the original frame (Testing only)	
	#cv2.imshow('Original',frame)

	#Convert to HSV
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	h, s, v = cv2.split(hsv)
	
	hue = cv2.absdiff(h,90)
	hue = cv2.subtract(90,hue)	
	hue = cv2.divide(hue,h_div)
	saturation = cv2.divide(s, s_div)
	value = cv2.divide(v,v_div)

	targetyness = cv2.multiply(hue,saturation)
	targetyness = cv2.multiply(targetyness, value)

	ret, targetyness = cv2.threshold(targetyness, 200,255,0) 
	mask = targetyness
	
	#Show the mask (Testing Only)
	#cv2.imshow('mask',mask)


	#Find the contours of the combined image
	discardImage, contours, hierarchy = cv2.findContours(targetyness,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)


	#Make sure that a contour region is found
	if len(contours) > 1:
		#find Biggest Contour region
		areas = [cv2.contourArea(c) for c in contours]
		max_index = np.argmax(areas)
		cnt=contours[max_index]
	
		#Find the smallest bounding box of the rectangle
		rect = cv2.minAreaRect(cnt)
		box = cv2.boxPoints(rect)
		box = np.int0(box)
		
		#find center of target for RoboRIO
		xCenter = (box[0][0] + box[1][0] + box[2][0] + box[3][0]) / 4
		yCenter = (box[0][1] + box[1][1] + box[2][1] + box[3][1]) / 4
		
		#These Calculations and draw settings are to help the driver lock onto the target
		xLocked = abs(xTarget - xCenter) < xError
		yLocked = abs(yTarget - yCenter) < yError
		
		#This here is just for drawing lines on the screen
		if(xLocked):
			cv2.line(frame,(xTarget,0),(xTarget,480),(0,0,255),3)
		else:
			cv2.line(frame,(xTarget,0),(xTarget,480),(255,0,0),3)
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
	#cv2.imshow("Show",frame)
	#Quit if q is pressed
   	if cv2.waitKey(1) & 0xFF == ord('q'):
		print exitKey
	return msg , frame, mask
	


def gen(value):
	"""Video streaming generator function."""
#	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#	soc.settimeout(2)
     
    # connect to remote host
#	try:
#		soc.connect((host, port))
#		print 'found target'
#		soc.send('#Found you\n')
	
#	except:
#		print("unable to connect")
#		sys.exit()
        while 1:
		if(value == 0):
			msg, CVframe, maskFrame = vision(cap)
#			try:
#				soc.send(msg)
#			except:
#	   			print 'Lost Connection with Roborio'
#				soc.connect((host, port))
#				print('found target')
#				soc.send("#Found you\n")
			frame = cv2.imencode('.jpg',CVframe,[IMWRITE_JPEG_QUALITY, 10])[1].tostring()
		elif(value == 1):
			ret, CVframe = cap_two.read()
			#if(ret == False):
			#	frame = polarBearError
			#else:
			frame = cv2.imencode('.jpg',CVframe,[IMWRITE_JPEG_QUALITY, 10])[1].tostring()
		elif(value == 2 ):
			ret, CVframe = cap_three.read()
			#if(ret == False):
			#	frame = polarBearError
			#else:
			frame = cv2.imencode('.jpg',CVframe,[IMWRITE_JPEG_QUALITY, 10])[1].tostring()
		else:
			msg, CVframe, maskFrame = vision(cap)
#			try:
#				soc.send(msg)
#			except:
#	   			print 'Lost Connection with Roborio'
#				soc.connect((host, port))
#				print('found target')
#				soc.send("#Found you\n")
			frame = cv2.imencode('.jpg',maskFrame,[IMWRITE_JPEG_QUALITY, 10])[1].tostring()	
		yield (b'--frame\r\n'
	       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(0),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_two')
def video_feed_two():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(1),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/video_feed_three')
def video_feed_three():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(2),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_mask')
def video_feed_mask():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(3),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/load_settings')
def load_settings():
	toReturn = "["
	print("Load_Settings Called")
	os.chdir("/home/ubuntu/2016-Vision/VideoStream/Presets")
	for file in glob.glob("*.txt"):
		f = open(file,"r")
		toReturn = toReturn + f.read() + ', '
	toReturn = toReturn[:len(toReturn) - 2]
	toReturn = toReturn + ']'
	return Response(toReturn)
@app.route('/updateValues')
def updateValues():
    global h_div
    global s_div
    global v_div
    global xTarget
    global yTarget
    global save_name
    global save_now
    h_div = request.args.get('h_div', 0, type=int)
    s_div = request.args.get('s_div', 0, type=int)
    v_div = request.args.get('v_div', 0, type=int)
    xTarget = request.args.get('xTarget', 0, type=int)
    yTarget = request.args.get('yTarget', 0, type=int)
    save_name = request.args.get('save_name', 0, type=str)
    save_now = request.args.get('save_now', 0, type=int)
    if(save_now == 1):
		f = open("/home/ubuntu/2016-Vision/VideoStream/Presets/" + save_name + ".txt", 'w')
		f.write('{\"name\": \"' + save_name 
		+ '\", \"h_div\":' + str(h_div) 
		+ ',\"s_div\":' + str(s_div)
		+ ',\"v_div\":' + str(v_div)
		+ ',\"xTarget\":' + str(xTarget)
		+ ',\"yTarget\":' + str(yTarget)
		+ '}')
    return 0

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5800, threaded=True)


cap.release()
cap_two.release()
cv2.destroyAllWindows()
print("Ended Feed")





