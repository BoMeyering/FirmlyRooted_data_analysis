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
file_list = os.listdir('PROP_ADAIR')

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




for file in file_list[:]:
# for file in ['47_02_4.JPG', '47_24_1.JPG', '47_24_2.JPG', '47_24_3.JPG', '47_51_4.JPG', '48_03_1.JPG']:
	A = blueThreshold('PROP_ADAIR/'+file, bin_range = 30, invert = True)
	th_midPt = int(A.shape[1]/2)
	A2 = cv2.medianBlur(A, 5)
	A2 = A2[510:,:] # set initial offest
	# A2 = A[510:,:] # set initial offest

	# cont, _ = cv2.findContours(A2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
	# blank = np.zeros(A2.shape, np.uint8)
	# for i in range(len(cont)):
	# 	cv2.drawContours(blank, cont, i, 120, 3)

	# cv2.namedWindow('test', cv2.WINDOW_NORMAL)
	# cv2.imshow('test', blank)
	# cv2.waitKey()
	# cv2.destroyAllWindows()



	#print(file)

	cont, shape = findLargeContour(A2, 100)
	cont = np.reshape(cont, (cont.shape[0], cont.shape[2]))

	blank = np.zeros(shape)
	cv2.fillPoly(blank, [cont], (255))

	# for contour in cont:
	# 	cv2.drawContours(blank, [contour], -1, 255, -1)
	# print(cont)


	# cv2.namedWindow('test', cv2.WINDOW_NORMAL)
	# cv2.imshow('test', blank)
	# cv2.waitKey(0)
	# cv2.destroyWindow('test')

	# vsums = np.sum(A2[:,th_midPt-150:th_midPt+150], 1, dtype = 'double')
	vsums = np.sum(A2, 1, dtype = 'double')
	# cv2.namedWindow('test', cv2.WINDOW_NORMAL)
	# cv2.imshow('test', A2)
	# cv2.waitKey()
	# cv2.destroyAllWindows()
	
	# hsums = np.sum(A2[:300,:], 0, dtype = 'double')
	# sums = np.cumsum(hsums)
	# area = simps(hsums)

	# wt_midPt = int(find_ge(sums, area/2))
	th_midPt = int(A.shape[1]/2)
	# avg_midPt = int(np.mean([wt_midPt, th_midPt]))

	# plt.plot(hsums, 'k')
	# plt.axvline(x = th_midPt)
	# plt.show()

	# vsums = np.sum(A2[:,th_midPt-150:th_midPt+150], 1, dtype = 'double')
		
	# plt.plot(vsums, 'k')
	# plt.show()

	# left = th_midPt-100
	# right = th_midPt+100
	# print(left,right)
	# A3 = A2[:, left:right]
	# print(A2.shape)
	# print(A3.shape)
	# cv2.namedWindow('test', cv2.WINDOW_NORMAL)
	# #cv2.imshow('test', A2[:,th_midPt-100:th_midPt+100])
	# cv2.imshow('test', A3)
	# cv2.waitKey()
	# cv2.destroyAllWindows()

	# plt.plot(vsums, 'k')
	# plt.axvline(x = th_midPt)
	# plt.show()

	diff = np.abs(np.diff(vsums, 2))/255
	# plt.plot(vsums, color = 'k') 
	# plt.show()
	for i in range(0, len(diff)):
		if diff[i] > 8 and vsums[i] > 1:
			print(i)
			A3 = A2[int(i+1):, :]
			#A3[:,th_midPt] = 255
			cv2.imwrite('data_files/'+file, A3)
			break

	#cv2.imwrite('data_files/'+file, A2[y:,])