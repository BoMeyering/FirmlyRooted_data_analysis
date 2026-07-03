import cv2
import math
from sympy.solvers import solve
from sympy import Symbol
import numpy as np
from scipy.spatial import distance_matrix


def findRadCenter(a, search_size):
	'''
	Takes a thresholded binary image
	Identifies the centering dot on stem face
	Returns a tuple of xy coordinates for center pixel
	'''
	assert type(a) == np.ndarray, "Error: 'a' is not a Numpy array."
	assert type(search_size) == int
	assert a.ndim == 2, "Error: 'a' is not a binary image."

	zero_mask = np.zeros(a.shape, dtype = 'uint8')
	cir_mask = cv2.circle(zero_mask, (int(zero_mask.shape[1]//2), int(zero_mask.shape[0]//2)), search_size, 255, -1)
	cir_mask_img = cv2.bitwise_and(a, a, mask=cir_mask)

	centers = cv2.HoughCircles(cir_mask_img, cv2.HOUGH_GRADIENT, 1, minDist=200, param1=60, param2=10, minRadius=10, maxRadius=30) # detect all circular objects in image
	print(centers)
	th_center = np.array([[zero_mask.shape[1]//2, zero_mask.shape[0]//2]])
	centers = np.uint16(np.around(centers))[0,:,0:2] # return nx2 matrix of candidate circle centers
	if type(centers) == None:
		return None
	dist = distance_matrix(centers, th_center)**2 # calculate squared distance matrix (penalizes larger distances)
	print(dist)
	#	Return best candidate center
	return centers[np.argmin(dist),]


def manualRadCenter(a, distance):
	'''
	Takes a thresholded binary image
	Identifies the centering dot on stem face
	Returns a tuple of xy coordinates for center pixel
	'''
	assert type(a) == np.ndarray, "Error: 'a' is not a Numpy array."
	assert type(distance) == int
	assert a.ndim == 2, "Error: 'a' is not a binary image."

	def doNothing(x):
		pass

	zero_mask = np.zeros(a.shape, dtype = 'uint8')
	center_circle = cv2.circle(zero_mask, (int(zero_mask.shape[1]//2), int(zero_mask.shape[0]//2)), distance, 255, -1)
	center_mask_img = cv2.bitwise_and(a, a, mask=center_circle)
	cv2.namedWindow('Center Circle Mask', cv2.WINDOW_KEEPRATIO)
	cv2.imshow('Center Circle Mask', center_mask_img)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	cv2.namedWindow('Hough Transform Track Bars', cv2.WINDOW_NORMAL)
	cv2.createTrackbar('distmin', 'Hough Transform Track Bars', 10, 300, doNothing)
	cv2.createTrackbar('param1', 'Hough Transform Track Bars', 10, 300, doNothing)
	cv2.createTrackbar('param2', 'Hough Transform Track Bars', 10, 300, doNothing)
	cv2.createTrackbar('minRadius', 'Hough Transform Track Bars', 10, 300, doNothing)
	cv2.createTrackbar('maxRadius', 'Hough Transform Track Bars', 10, 300, doNothing)

	while True:
		cv2.namedWindow('circle detection', cv2.WINDOW_NORMAL)
		distmin = cv2.getTrackbarPos('distmin', 'Hough Transform Track Bars')
		param1 = cv2.getTrackbarPos('param1', 'Hough Transform Track Bars')
		param2 = cv2.getTrackbarPos('param2', 'Hough Transform Track Bars')
		minRadius = cv2.getTrackbarPos('minRadius', 'Hough Transform Track Bars')
		maxRadius = cv2.getTrackbarPos('maxRadius', 'Hough Transform Track Bars')
		center_mask_cp = center_mask_img.copy()
		circles = cv2.HoughCircles(center_mask_cp, cv2.HOUGH_GRADIENT, 1, distmin, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
		img_cp = a.copy()
		img_cp = img_cp[..., np.newaxis]
		img_cp = np.concatenate((img_cp, np.zeros(a.shape)[...,np.newaxis], np.zeros(a.shape)[...,np.newaxis]), axis = 2)
		if circles is not None:
			circles = np.uint16(np.around(circles))
			for i in circles[0, :]:
				cv2.circle(img_cp, (i[0], i[1]), i[2], (0, 255, 0), 2)
				cv2.circle(img_cp, (i[0], i[1]), 2, (0, 0, 255), 3)
			cv2.imshow('circle detection', img_cp)
		elif circles is None:
			cv2.imshow('circle detection', img_cp)

		key = cv2.waitKey(25)
		if key == ord('q'):
			break

	cv2.destroyAllWindows()

	th_center = np.array([[zero_mask.shape[1]//2, zero_mask.shape[0]//2]])
	centers = np.uint16(np.around(circles))[0,:,0:2] # return nx2 matrix of candidate circle centers
	if type(centers) == None:
		return None
	dist = distance_matrix(centers, th_center)**2 # calculate squared distance matrix (penalizes larger distances)
	print(centers)
	print(dist)
	#	Return best candidate center
	return centers[np.argmin(dist),]



def radialMask(a, edge_points, radius, center, **kwargs):
	'''
	Takes a thresholded binary image
	Crops the numpy array with set pixel radius from center point
	

	'''

	assert type(a)==np.ndarray, "Error: 'a' is not a Numpy array."
	assert type(edge_points)==np.ndarray and edge_points.ndim==2, "Error: 'a' has an incorrect number of dimensions"
	assert type(radius)==int and radius <= np.amin(a.shape)/2, "Error: radius is too large"

	zero_mask = np.zeros(a.shape)
	cv2.circle(a, center, radius, 255)
	a_masked = cv2.bitwise_and(a, a, mask = zero_mask)
	a_cropped = a_masked[(center[1]-radius):(center[1]+radius), (center[0]-radius):(center[0]+radius)]

	return a_cropped