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


cap = cv2.VideoCapture(22)
cap.set(3,640)
cap.set(4,480)
while 1:
	ret, frame = cap.read()
	cv2.imshow('frame',frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		print exitKey
