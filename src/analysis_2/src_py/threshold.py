#	image thresholding

import cv2
import numpy as np
from matplotlib import pyplot as plt

def manualThreshold(filename, output='array', invert=True):
	'''
	Manual, interactive thresholding of images
	Selects for pixels in chosen range
	Returns a thresholded image Numpy Array
	A dictionary of HSV threshold values chosen for the image
	or both an array and dictionary
	'''
	assert output == 'array' or output == 'values' or output == 'both'
	assert invert==True or invert==False
	rawImg = cv2.imread(filename)
	hsvImg = cv2.cvtColor(rawImg, cv2.COLOR_BGR2HSV)

	#empty function
	def _doNothing(x):
		pass
    #create trackbar window and set starting values
	cv2.namedWindow('Track Bars', cv2.WINDOW_NORMAL)
	cv2.createTrackbar('Hmin', 'Track Bars', 0, 179, _doNothing)
	cv2.createTrackbar('Smin', 'Track Bars', 0, 255, _doNothing)
	cv2.createTrackbar('Vmin', 'Track Bars', 0, 255, _doNothing)
	cv2.createTrackbar('Hmax', 'Track Bars', 0, 179, _doNothing)
	cv2.createTrackbar('Smax', 'Track Bars', 0, 255, _doNothing)
	cv2.createTrackbar('Vmax', 'Track Bars', 0, 255, _doNothing)
	cv2.setTrackbarPos('Hmax', 'Track Bars', 179)
	cv2.setTrackbarPos('Smax', 'Track Bars', 255)
	cv2.setTrackbarPos('Vmax', 'Track Bars', 255)

	cv2.namedWindow('Raw Image', cv2.WINDOW_KEEPRATIO)
	cv2.namedWindow('HSV Image', cv2.WINDOW_KEEPRATIO)
	cv2.namedWindow('Thresholding', cv2.WINDOW_KEEPRATIO)

	cv2.imshow('Raw Image', rawImg)
	cv2.imshow('HSV Image', hsvImg)

	while True:
 		Hmin = cv2.getTrackbarPos('Hmin', 'Track Bars')
 		Smin = cv2.getTrackbarPos('Smin', 'Track Bars')
 		Vmin = cv2.getTrackbarPos('Vmin', 'Track Bars')
 		Hmax = cv2.getTrackbarPos('Hmax', 'Track Bars')
 		Smax = cv2.getTrackbarPos('Smax', 'Track Bars')
 		Vmax = cv2.getTrackbarPos('Vmax', 'Track Bars')

 		fImg = cv2.inRange(hsvImg, (Hmin, Smin, Vmin), (Hmax, Smax, Vmax))
 		cv2.imshow('Thresholding', fImg)
 		key = cv2.waitKey(25)
 		if key == ord('q'):
 			break

	cv2.destroyAllWindows()
	
	hsvValues = {'HSVmin': (Hmin, Smin, Vmin), 'HSVmax': (Hmax, Smax, Vmax)}
	if invert==True:
		fImg = cv2.bitwise_not(fImg)

	if output == 'array':
		return fImg
	elif output == 'values':
		return mask_values
	elif output == 'both':
		return fImg, hsvValues




def blueThreshold(filename, output='array', bin_range=10, invert=True, show_plot=False):
	'''
	Automatic image thresholding of clean images taken against bluescreen
	Selects for pixels within the blue range of HSV colorspace on either side of the blue hue histogram peak
	Returns a thresholded image Numpy Array
	Or a dictionary of HSV threshold values for the image
	'''
	assert output == 'array' or output == 'values' or output == 'both'
	assert invert==True or invert==False
	rawImg = cv2.imread(filename)
	hsvImg = cv2.cvtColor(rawImg, cv2.COLOR_BGR2HSV)

	hist = cv2.calcHist(hsvImg, [0], None, [180], [0,180])
	if show_plot == True:
		plt.title('Hue Histogram')
		plt.plot(hist, color = 'blue')
		plt.show()

	maxHue = np.argmax(hist)
	hueRange = (maxHue-bin_range, maxHue+bin_range)

	hsvValues = {'HSVmin': (int(hueRange[0]), 0, 0), 'HSVmax': (int(hueRange[1]), 255, 255)}

	fImg = cv2.inRange(hsvImg, hsvValues.get('HSVmin'), hsvValues.get('HSVmax'))

	if invert==True:
		fImg = cv2.bitwise_not(fImg)

	if output == 'array':
		return fImg
	elif output == 'values':
		return hsvValues
	elif output == 'both':
		return fImg, hsvValues


