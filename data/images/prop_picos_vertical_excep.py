import sys
sys.path.insert(0, '../../../../github_repos/tria/src/tria/')
from calc import unitVectors, polyPoints
from threshold import manualThreshold, blueThreshold
from mask import findRadCenter
import numpy as np
import cv2
import time
from scipy.integrate import simps
import os

import pandas as pd

import matplotlib.pyplot as plt
import bisect
file_list = os.listdir('PROP_PICOS')

res = []

def find_ge(a, x):
	i = bisect.bisect_left(a, x)
	if i != len(a):
		return i
	raise ValueError


def findLargeContour(a, search_dist):
	'''
	Pass in a binary image array of the features in white, background in black
	returns the y index of the minimum y index within a scope dictated by the center of the image and the search distance
	'''

	midPt = int(a.shape[1]/2)
	a2 = a[:500, midPt-search_dist:midPt+search_dist]

	# cv2.namedWindow('test', cv2.WINDOW_NORMAL)
	# cv2.imshow('test', a2)
	# cv2.waitKey()
	# cv2.destroyAllWindows()


	contours, hier = cv2.findContours(a2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
	cont_shapes = np.array([np.array(i.shape) for i in contours])
	#print(cont_shapes)
	idx = np.argmax(cont_shapes[:,0])
	struct = contours[idx]
	#struct = np.reshape(struct, (struct.shape[0], struct.shape[2]))

	return (struct, a2.shape)

	# blank = np.zeros(a2.shape, np.uint8)

	# for i in range(len(contours)):
	# 	#v2.drawContours(blank, hull, i, 255, 3)
	# 	cv2.drawContours(blank, contours, i, 120, 3)

	# cv2.namedWindow('test', cv2.WINDOW_NORMAL)
	# cv2.imshow('test', blank)
	# cv2.waitKey()
	# cv2.destroyAllWindows()

	#return np.min(struct[:,1])

for file in ['47_02_4.JPG', '47_24_1.JPG', '47_24_2.JPG', '47_24_3.JPG', '47_51_4.JPG', '48_03_1.JPG', '48_25_5.JPG', '48_37_3.JPG', '48_37_4.JPG', '48_39_0.JPG',]:
	A = blueThreshold('PROP_PICOS/'+file, bin_range = 30, invert = True)
	th_midPt = int(A.shape[1]/2)
	A2 = cv2.medianBlur(A, 5)
	A2 = A2[510:,:] # set initial offest
	cv2.imwrite('data_files/'+file, A2)
