######################
#Binary Tiff Splitter#
######################

import pims
import imageio
import numpy as np
import os

def tiff_splitter(filename, target_dir = None, output_names = None, invert_images=False, return_data = False):
	"""
	Takes a multipage, binary tiff file and splits it into individual tiff images
	Can save the tiff images to the directory of choice
	Additional arguments for inverting the images and returning the resulting numpy arrays of pixel values
	"""

	assert os.path.exists(filename), "This file does not exist"
	# load tiff_stack
	img_stack = pims.TiffStack(filename)

	# target directory assertion
	if target_dir is not None:
		try:
			assert os.path.exists(target_dir)
		except AssertionError:
			print(f"Making directory '{target_dir}' for image output")
			os.mkdir(target_dir)
	if target_dir[-1] != "/":	# append forward slash if not present
		target_dir += "/"

	else:
		target_dir = os.getcwd()

	# name length assertion
	if output_names is not None:
		assert iter(output_names), "Error: output_names is not iterable."
		assert len(output_names) == len(img_stack), "Error: len(output_names) != len(img_stack)"
	else:
		output_names = [str(f"img_{i+1}.tif") for i in range(len(img_stack))]
		print(output_names)

	def _stack_split(img_stack, invert = invert_images):
		"""
		Takes a stack of tiff images
		splits them into numpy arrays
		returns a list of the image arrays
		"""
		results = []
		for i in range(len(img_stack)):
			img = np.array(img_stack[i], np.uint8)
			if invert:
				img = _img_invert(img)
			results.append(img)
		return results

	def _img_invert(array):
		"""
		Takes a binary image in the form of a numpy array
		And inverts it, i.e. black pixels become white and vice-versa
		"""
		assert set(np.unique(array)) == {0, 255}, "Image is not a binary image"
		x = array /255		# descale the image
		x = x.astype(int)
		x_inv_scale = np.where((x==0)|(x==1), x^1, x)*255		# invert and rescale the image
		x_inv_scale = np.array(x_inv_scale, np.uint8)
		return x_inv_scale

	def _save_image(img_list, target_dir, output_names):
		for i in range(len(img_list)):
			imageio.imwrite(target_dir + output_names[i], img_list[i])

	# Run main functionality
	stack_list = _stack_split(img_stack)
	_save_image(stack_list, target_dir, output_names)
	if return_data:
		return np.stack(stack_list, axis = 2)
		print("Tiff file split!")
	else:
		print("Tiff file split!")
