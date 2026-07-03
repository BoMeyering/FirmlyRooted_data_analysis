import multiprocessing

import numpy as np
import math
from sympy.solvers import solve
from sympy import Symbol
import time
import cv2
from tqdm.auto import tqdm
from multiprocessing import Process

def unitVectors(slices):
	'''
	Takes an integer angle slices argument
	Returns a numpy array of unit vectors 
	For the specified number of slices
	'''
	assert type(slices)==int, "Error: 'step' is not an integer"

	step = 360/slices*math.pi/180 # angle step in radians
	rad_slices = np.cumsum([step]*slices)
	rad_slices = np.insert(rad_slices, 0, 0) # inserts a '0' at the beginning of the array
	unit_vectors = np.array([(math.cos(rad), math.sin(rad)) for rad in rad_slices]) # calculate unit vectors

	return unit_vectors

def polyPoints(vectors, radius, center):
	'''
	Takes a numpy array of unit vectors (shape = (slices+1, 2))
	Scales them up according to image center and radius
	'''
	slices = vectors.shape[0]-1
	step = 360/slices*math.pi/180	# Find step in radians
	tan_rad = step/2	# find the angle in radians to calculate the tangent line
	sfact = math.sqrt(math.tan(tan_rad)**2 + 1)*radius	# unit vector scale factor for where the unit vector intersects the tangent line for a circle with set radius
	scaled_points = center + vectors*sfact	# Scale unit vectors

	poly_points = np.empty((vectors.shape[0]-1, 1, 3, 2), dtype='int')

	for i in range(0, slices):
		poly_points[i] = np.around([[scaled_points[i], scaled_points[i+1], center]])

	step = 360/(len(vectors)-1)
	offset = step/2
	angles = []
	for i in range(len(vectors)-1):
		angles.append((360-offset) - i*step)

	return poly_points, angles

def getRings(radii, shape, center):
	"""

	:param radii:
	:param shape:
	:param center:
	:return: a numpy array of shape (len(radii), shape[0], shape[1])
	"""
	if len(shape) > 2:
		raise ValueError(f"Argument 'shape' is of len {len(shape)} which is invalid for binary images. "\
						 f"Please pass in a tuple of len=2"
						 )
	# if not np.all(np.array([type(r)==int for r in radii])):
	# 	raise ValueError(f"Argument 'radii' must only contain integer types.")
	coords = np.array([[0, 0],
					   [shape[1], shape[0]]])
	center_a = np.array([[center[0], center[1]]])

	min_dst = np.min(np.abs(np.subtract(coords, center_a)))

	if np.max(radii) > min_dst:
		raise ValueError(f"The largest element of argument 'radii' ({np.max(radii)}) > min_dst to image edge ({min_dst}) from center point {center}. "\
						 f"Redefine center point or ensure that all radii passed are smaller than {min_dst}")

	radii.sort()
	rings = np.empty((len(radii), shape[0], shape[1]))
	for i in range(len(radii)):
		zero_mask = np.zeros(shape, np.uint8)
		if i == 0:
			ring = cv2.circle(zero_mask.copy(), center, radii[0], 255, -1)
			rings[i, :, :] = ring

		elif i > 0:
			circle_mask = cv2.circle(zero_mask.copy(), center, radii[i], 255, -1)
			inner_circle = cv2.circle(zero_mask.copy(), center, radii[i-1], 255, -1)
			ring = cv2.bitwise_xor(circle_mask, inner_circle)
			rings[i, :, :] = ring

	return rings

def getSlices(points, shape):
	"""

	:param points:
	:return:
	"""
	if len(points) == 0:
		raise ValueError(f"Argument 'points' contains no polyPoints. "\
						 f"Please pass in numpy array with at least one set of polygon points.")
	if len(shape) > 2:
		raise ValueError(f"Argument 'shape' is of len {len(shape)} which is invalid for binary images. "\
						 f"Please pass in a tuple of len=2"
						 )

	slices = np.empty((len(points), shape[0], shape[1]))
	for i in range(len(points)):
		points[i]
		slice_mask = np.zeros(shape, np.uint8)
		slice = cv2.fillPoly(slice_mask, points[i], 255)
		slices[i, :, :] = slice

	return slices

def get_radial_masks(rings, slices, shape):
	"""

	:param rings:
	:param slices:
	:return:
	"""
	# radial_masks = np.empty((len(rings)*len(slices), shape[0], shape[1]))
	step = len(slices)
	for i, ring in enumerate(rings):
		for j, slice in enumerate(slices):
			masked_slice = cv2.bitwise_and(ring, slice).astype(np.uint8)
			# radial_masks[i*step+j,:,:] = masked_slice

			yield masked_slice, (i, j)

def radialMask(rings, slices, indices):
	masked_slice = cv2.bitwise_and(rings[indices[0]], slices[indices[1]])

	return masked_slice

def unitSquare(slices):
	'''
	Takes an integer of slices to compute
	slices must be a multiple of 8
	Slices is an integer of the number of 'pie' slices around the origin
	Returns a numpy array of points that intersect with scaled unit vectors determined by slices
	This is *much* slower and less flexible than using a combination of unitVectors and polyPoints
	'''
	t1 = time.time()
	assert type(slices) == int, "Error: 'slices' is not of type int."
	slice_rng = [i for i in range(8, 121, 8)]
	assert slices in slice_rng, "Error: 'slices' is out of range or not a multiple of 8."

	ang_slices = np.cumsum([360/slices]*slices) # determine slices in degrees
	idx = np.min(np.where(ang_slices >= 270)) # Identify the minimum index for angle rolling
	ang_slices = (np.roll(ang_slices, slices-idx)) # roll angles
	rad_slices = ang_slices*math.pi/180 # convert to radians
	unit_vectors = np.array([(math.cos(ang), math.sin(ang)) for ang in rad_slices]) #calculate unit vectors
	edge_points = np.empty((slices, 2))
	t2 = time.time()
	print(f"first diff = {t2-t1}")
	# solve unit vectors for t at unit box points
	# for lines (1,0), (0,1), (-1,0), (0,-1)
	# x = 1, y = 1, x = -1, y = -1 
	
	for i in range(0, unit_vectors.shape[0]):
		t3 = time.time()
		vec = unit_vectors[i]
		t = Symbol('t')
		if ang_slices[i] > 0 and ang_slices[i] <= 45:
			t = solve(t*vec[0]-1)[0]
		elif ang_slices[i] > 45 and ang_slices[i] <=135:
			t = solve(t*vec[1]-1)[0]
		elif ang_slices[i] > 135 and ang_slices[i] <=225:
			t = solve(t*vec[0]+1)[0]
		elif ang_slices[i] > 225 and ang_slices[i] <=315:
			t = solve(t*vec[1]+1)[0]
		elif ang_slices[i] > 315 and ang_slices[i] <=360:
			t = solve(t*vec[0]-1)[0]
		pts = np.array([t*vec[0], t*vec[1]])
		edge_points[i,:] = pts
		t4 = time.time()
		print(f"loop time diff = {t4-t3}")
	return edge_points


def getIntegralDepth(a):
	"""
	Takes a binary cropped image as input and returns a pixel depth at which half of the integrated density lies
	i.e. the midpoint of the root density
	"""

	from scipy.integrate import simps
	import cv2
	import numpy as np
	import matplotlib.pyplot as plt
	import bisect

	def _find_ge(a, x):
		i = bisect.bisect_left(a, x)
		if i != len(a):
			return i
		raise ValueError
	
	vsums = np.sum(a,axis = 1,dtype = 'double')
	area = simps(vsums)
	cum_sums = np.cumsum(vsums)
	idx = _find_ge(cum_sums, int(area/2))

	return idx

if __name__ == '__main__':

	def show_img(img):
		cv2.namedWindow('test', cv2.WINDOW_NORMAL)
		cv2.imshow('test', img)
		cv2.waitKey()
		cv2.destroyAllWindows()
	cores = multiprocessing.cpu_count
	center_point = (1500, 1500)
	img_shape = (3000, 3000)
	radii = [int(i) for i in (np.rint([i * 1393 / 30 for i in range(1, 31)]))]

	max_radius = 1393
	max_radius = 1000

	vecs = unitVectors(90)
	# print(len(vecs))



	points, angles = polyPoints(vecs, max_radius, center_point)
	# print(len(points))
	# print(len(angles))
	print(angles)

	rings = getRings(radii, img_shape, center_point)

	slices = getSlices(points, img_shape)

	masked_slices = get_radial_masks(rings, slices, img_shape)
	for i in tqdm(range(len(rings)*len(slices))):
		radial_mask = next(masked_slices)
	# 	print(radial_mask)




	# for i in range(1, len(radii)):
	# 	print(i)
	# 	zero_mask = np.zeros(img_shape, np.uint8)
	# 	if i == 1:
	# 		print(radii[i])
	# 		ring = cv2.circle(zero_mask.copy(), center_point, radii[i], 255, -1)
	# 		show_img(ring)
	# 	elif i > 1:
	# 		print(radii[i])
	# 		circle_mask = cv2.circle(zero_mask.copy(), center_point, radii[i], 255, -1)
	# 		# show_img(circle_mask)
	# 		inner_circle = cv2.circle(zero_mask.copy(), center_point, radii[i-1], 255, -1)
	# 		# show_img(inner_circle)
	# 		ring = cv2.bitwise_xor(circle_mask, inner_circle)
	# 		show_img(ring)
	# 		# circle_mask = cv2.bitwise_xor(circle_mask, inner_circle)
	# 	# show_img(circle_mask)
	# 	for vecs in points:
	# 		# zero_mask = zero_mask.copy()
	# 		# show_img(zero_mask)
	# 		slice_mask = np.zeros(img_shape, np.uint8)
	# 		pts = np.array([[100, 350], [165, 350], [165, 240]], np.int32)
	# 		cv2.fillPoly(slice_mask, vecs, 255)
	#
	# 		masked = cv2.bitwise_and(ring, ring, mask=slice_mask)
	#
	# 		show_img(masked)





