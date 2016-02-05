import numpy as np
import cv2

xError = 24
yError = 24
xTarget = 320
yTarget = 200 

cap = cv2.VideoCapture(0)



while(True):
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
	cv2.imshow("Show",frame)
	#Quit if q is pressed
   	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	print (msg)
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
