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


xError = 24
yError = 24
xTarget = 320
yTarget = 180
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

#cap.set(CV_CAP_PROP_EXPOSURE_AUTO,1)
font = cv2.FONT_HERSHEY_SIMPLEX


#cap.set(15,100)
cap.set(14,0)

app = Flask(__name__)

global h_min
global h_max
global s_min
global s_max
global v_min
global v_max
global save_name
global save_now

h_min = 30
h_max = 89
s_min = 46
s_max = 125
v_min = 108
v_max = 255
save_name = ""
save_now = 0

pandaBearError = open("/home/ubuntu/2016-Vision/VideoStream/templates/PandaBearError.jpg",'rb').read()
polarBearError = open("/home/ubuntu/2016-Vision/VideoStream/templates/PolarBearError.jpg",'rb').read()

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('indexTwo.html')


def vision(cap):
	try:
		ret, frame = cap.read()
	#	if(ret == False):
	#	return "#Error Proccessing Vision",pandaBearError, pandaBearError
		global h_min
		global h_min
		global s_min
		global s_max
		global v_min
		global v_max
		# show the original frame (Testing only)	
		#cv2.imshow('Original',frame)
	
		#do conversions for the mask
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		lower_green = np.array([h_min, s_min, v_min]) 
		upper_green = np.array([h_max, s_max, v_max])
	
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
			cnt = None
			possibleCnt = []
			#loop through all accepted contours find potential target candidates
			#do not consider contours that dont meet all requirements
			for cont in contours:
				approx = cv2.approxPolyDP(cont,0.01*cv2.arcLength(cont,True),True)
				if not (abs(len(approx) - 8) <=1):
					continue
				if cv2.contourArea(cont)< 100:
					continue
			#Put the objects into the possibleCnt Array in a sorted manner
				if len(possibleCnt) == 0 or cv2.contourArea(cont) < cv2.contourArea(possibleCnt[len(possibleCnt)-1]):
					possibleCnt.append(cont)
					continue
				for i in range(0,len(possibleCnt)):
					if cv2.contourArea(cont)> cv2.contourArea(possibleCnt[i]):
						possibleCnt.insert(i,cont)

						
			#loop through all candidates pick the best one
			if len(possibleCnt) > 0:
				cnt = possibleCnt[0]
			for cont in possibleCnt:
				#cv2.drawContours(frame,[cont],0,(0,255,0),-1)	
				if cv2.contourArea(cont) < cv2.contourArea(cnt):
					if cv2.arcLength(cont,True) > cv2.arcLength(cnt,True):
						cnt = cont				
			cv2.drawContours(frame,[cnt],0,(0,0,0),-1)

	
			if cnt == None:
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
			
			#This here is just for drawing lines on the screen
			if(xLocked):
				cv2.line(frame,(320,0),(320,480),(0,0,255),3)
			else:
				cv2.line(frame,(320,0),(320,480),(255,0,0),3)
			if(yLocked):
				cv2.line(frame,(0,yTarget),(640,yTarget),(0,0,255),3)
			else:				
				cv2.line(frame,(0,yTarget),(640,yTarget),(255,0,0),3)
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
	except:
		print("Unable to process frame")
	
	
def gen(value):
	"""Video streaming generator function."""
	soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	soc.settimeout(2)
	dataSend = True
    # connect to remote host
	try:
		soc.connect((host, port))
		print 'found target'
		soc.send('#Found you\n')
	
	except:
		print("unable to connect")
        while 1:
		if(dataSend == False):
			try:
				soc.connect((host,port))
				print('found target')
				soc.send('#Recovered Transmission\n')
				dataSend = True
			except:
				print("unable to connect")
		if(value == 0):
			msg, CVframe, maskFrame = vision(cap)
			try:
				soc.send(msg)
			except:
	   			print 'data send failed'
				dataSend = False
			frame = cv2.imencode('.jpg',CVframe,[IMWRITE_JPEG_QUALITY, 10])[1].tostring()
		elif(value == 1):
			ret, CVframe = cap_two.read()
#			if(ret == False):
#				frame = polarBearError
#			else:
			frame = cv2.imencode('.jpg',CVframe,[IMWRITE_JPEG_QUALITY, 10])[1].tostring()
		elif(value ==2):
			ret, CVframe = cap_three.read()
#			if(ret == False):
#				frame = pandaBearError
#			else:
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
    global h_min
    global h_max
    global s_min
    global s_max
    global v_min
    global v_max
    global save_name
    global save_now
    h_min = request.args.get('h_min', 0, type=int)
    h_max = request.args.get('h_max', 0, type=int)
    s_min = request.args.get('s_min', 0, type=int)
    s_max = request.args.get('s_max', 0, type=int)
    v_min = request.args.get('v_min', 0, type=int)
    v_max = request.args.get('v_max', 0, type=int)
    save_name = request.args.get('save_name', 0, type=str)
    save_now = request.args.get('save_now', 0, type=int)
    if(save_now == 1):
		f = open("/home/ubuntu/2016-Vision/VideoStream/Presets/" + save_name + ".txt", 'w')
		f.write('{\"name\": \"' + save_name 
		+ '\", \"h_min\":' + str(h_min) 
		+ ',\"h_max\":' + str(h_max)
		+ ',\"s_min\":' + str(s_min)
		+ ',\"s_max\":' + str(s_max)
		+ ',\"v_min\":' + str(v_min)
		+ ',\"v_max\":' + str(v_max) 
		+ '}')
    return 0

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5800, threaded=True)


cap.release()
cap_two.release()
cv2.destroyAllWindows()
print("Ended Feed")






