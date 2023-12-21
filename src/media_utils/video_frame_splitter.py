######################
#movie_frame_splitter#
######################

import pims
import imageio
import numpy as np
import os
import glob

def movie_splitter(filename, target_dir):
	"""
	Take a movie file supported by PIMS.ImageIOReader
	Split into individual frames
	Return a directory of greyscale images
	"""
	import pims
	import imageio
	import numpy as np
	import os

	if not os.path.exists(filename):
		raise FileNotFoundError(f"The file {filename} does not exist")

	elif not os.path.exists(target_dir):
		print(f"Making directory '{target_dir}' for image output")
		os.mkdir(target_dir)

	vid = pims.ImageIOReader(filename)
	t = vid.frame_rate
	vlen = len(vid)-1

	target_dir += "/"
	print(target_dir)

	for fr_i in range(vlen):
		frame = vid[fr_i][:,:,0]
		imageio.imwrite(f"{target_dir}{fr_i}.jpeg", frame)

	print(f"Video {filename} frames captured!")


# vid_list = glob.glob('*.mp4')
# dir_list = []
# for vid_name in vid_list:
# 	name = vid_name.split('_overlay')[0] + "_images"
# 	dir_list.append(name)

# print(dir_list)
# print(vid_list)

# for i in range(len(vid_list)):
# 	movie_splitter(vid_list[i], dir_list[i])

print("Completed!")

if __name__ == '__main__':
	root_dir = "../../data/excavation_footage/PROP_ADAIR"
	vid_list = glob.glob('*.MOV', root_dir=root_dir)
	path_list = []
	for vid_name in vid_list:
		name = vid_name.split('.')[0] + "_still.png"
		image_path = os.path.join("../../data/images/PROP_ADAIR/overlay_stills", name)
		path_list.append(image_path)

		vid = pims.ImageIOReader(os.path.join(root_dir, vid_name))
		t = vid.frame_rate
		vlen = len(vid)-1
		print(vlen)

		frame = vid[0]
		imageio.imwrite(image_path, frame)

		print(f"Video {name} frame captured")
