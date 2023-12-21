from glob import glob
import os
from scipy.integrate import simps
import numpy as np
import bisect
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import os

def getIntegralDepth(a):
	"""
	Takes a binary cropped image as input and returns a pixel depth at which half of the integrated density lies
	i.e. the midpoint of the root density
	"""

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
	bin_img_dir = './data/images/PROP_ADAIR/vertical_threshold_cropped'
	bin_img_names = glob('*.JPG', root_dir=bin_img_dir)

	res = []
	# print(adair_list)
	for file in bin_img_names:
		#print(file)
		A = cv2.imread(os.path.join(bin_img_dir, file), cv2.IMREAD_UNCHANGED)
		res.append(getIntegralDepth(A))

	df_adair = pd.DataFrame({"filename": bin_img_names, "pixel_depth": res})

	bin_img_dir = './data/images/PROP_PICOS/vertical_threshold_cropped'
	bin_img_names = glob('*.JPG', root_dir=bin_img_dir)
	res = []
	# print(picos_list)
	for file in bin_img_names:
		A = cv2.imread(os.path.join(bin_img_dir, file), cv2.IMREAD_UNCHANGED)
		res.append(getIntegralDepth(A))

	df_picos = pd.DataFrame({'filename': bin_img_names, 'pixel_depth': res})

	df_adair.to_csv('./data/images/prop_adair_integral_pixel_depths.csv')
	df_picos.to_csv('./data/images/prop_picos_integral_pixel_depths.csv')


