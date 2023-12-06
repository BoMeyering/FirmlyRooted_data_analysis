import sys
sys.path.insert(0, '../../../../github_repos/tria/src/tria/')
#sys.path.insert(0, '../src/tria/data/')
from calc import unitVectors, polyPoints
from threshold import manualThreshold, blueThreshold
from mask import findRadCenter
import numpy as np
import cv2
#import time
#from scipy.integrate import simps
import os
from itertools import permutations
from scipy.spatial import distance_matrix

file_list = os.listdir("./PROP_ADAIR")

def doNothing(x):
    pass

for file in file_list[:10]:
	print('./PROP_ADAIR/'+file)
	src = cv2.imread('./PROP_ADAIR/'+file)
	#A2 = blueThreshold('./PROP_ADAIR/'+file, output = 'both', bin_range = 15, invert=False)
	A2 = manualThreshold('./PROP_ADAIR/'+file, output = 'both', invert=False)
	print(A2[1])

	cv2.namedWindow('threshold', cv2.WINDOW_NORMAL)
	cv2.imshow('threshold', A2[0])
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	#A2 = cv2.medianBlur(A[0], 5)
	zero_mask = np.zeros(A2[0].shape, dtype = 'uint8')
	center_circle = cv2.circle(zero_mask, (int(zero_mask.shape[1]//2), int(zero_mask.shape[0]//2)), 100, 255, -1)
	center_mask_img = cv2.bitwise_and(A2[0], A2[0], mask=center_circle)

	cv2.namedWindow('canny', cv2.WINDOW_NORMAL)
	cv2.imshow('canny', center_mask_img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	for i in [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]:
		circles = cv2.HoughCircles(center_mask_img, cv2.HOUGH_GRADIENT_ALT,3, minDist = 300, param1=300,param2=i, minRadius=5, maxRadius=45)
		print(circles)

		if circles is not None:
			for circle in circles[0]:
				print(circle)
				center_x, center_y, radius = circle
				print(center_x, center_y, radius)
				cv2.circle(src, (int(center_x), int(center_y)), int(radius) ,(0, 255, ), 2)
				cv2.circle(src, (int(center_x), int(center_y)), 1 ,(0, 0, 255), 2)
		cv2.namedWindow('A2', cv2.WINDOW_NORMAL)
		cv2.imshow("A2", src)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
	else:
		print("No circles found for ", file)
		pass



# 	zero_mask = np.zeros(A2.shape, dtype = 'uint8')
# 	center_circle = cv2.circle(zero_mask, (int(zero_mask.shape[1]//2), int(zero_mask.shape[0]//2)), 500, 255, -1)
# 	center_mask_img = cv2.bitwise_and(A2, A2, mask=center_circle)
# 	cv2.namedWindow('Center Circle Mask', cv2.WINDOW_KEEPRATIO)
# 	cv2.imshow('Center Circle Mask', center_mask_img)
# 	cv2.waitKey(0)
# 	cv2.destroyAllWindows()

# 	cv2.namedWindow('Hough Transform Track Bars', cv2.WINDOW_NORMAL)
# 	cv2.createTrackbar('distmin', 'Hough Transform Track Bars', 10, 300, doNothing)
# 	cv2.createTrackbar('param1', 'Hough Transform Track Bars', 10, 300, doNothing)
# 	cv2.createTrackbar('param2', 'Hough Transform Track Bars', 1, 10, doNothing)
# 	cv2.createTrackbar('minRadius', 'Hough Transform Track Bars', 10, 300, doNothing)
# 	cv2.createTrackbar('maxRadius', 'Hough Transform Track Bars', 10, 300, doNothing)

# 	while True:
# 		cv2.namedWindow('circle detection', cv2.WINDOW_NORMAL)
# 		distmin = cv2.getTrackbarPos('distmin', 'Hough Transform Track Bars')
# 		param1 = cv2.getTrackbarPos('param1', 'Hough Transform Track Bars')
# 		param2 = cv2.getTrackbarPos('param2', 'Hough Transform Track Bars')
# 		minRadius = cv2.getTrackbarPos('minRadius', 'Hough Transform Track Bars')
# 		maxRadius = cv2.getTrackbarPos('maxRadius', 'Hough Transform Track Bars')
# 		center_mask_cp = center_mask_img.copy()
# 		circles = cv2.HoughCircles(center_mask_cp, cv2.HOUGH_GRADIENT_ALT, 1, distmin, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
# 		print(circles)
# 		img_cp = A2.copy()
# 		img_cp = img_cp[..., np.newaxis]
# 		img_cp = np.concatenate((img_cp, np.zeros(A2.shape)[...,np.newaxis], np.zeros(A2.shape)[...,np.newaxis]), axis = 2)
# 		if circles is not None:
# 			circles = np.uint16(np.around(circles))
# 			for i in circles[0, :]:
# 				cv2.circle(img_cp, (i[0], i[1]), i[2], (0, 255, 0), 2)
# 				cv2.circle(img_cp, (i[0], i[1]), 2, (0, 0, 255), 3)
# 			cv2.imshow('circle detection', img_cp)
# 		elif circles is None:
# 			cv2.imshow('circle detection', img_cp)

# 		key = cv2.waitKey(25)
# 		if key == ord('q'):
# 			break

# # Define image center from detected circle
# 	th_center = np.array([[zero_mask.shape[1]//2, zero_mask.shape[0]//2]])
# 	centers = np.uint16(np.around(circles))[0,:,0:2]
# 	dist = distance_matrix(centers, th_center)**2
# 	print(dist)
# 	print(centers[np.argmin(dist),])
# 	#center = (circles[0,0,0], circles[0,0,1])
# 	cv2.destroyAllWindows()

	

	# center = findRadCenter(A2, 200)
	# print(center)