import sys
sys.path.insert(0, '../../../../github_repos/tria/src/tria/')
from threshold import manualThreshold, blueThreshold
from mask import findRadCenter, manualRadCenter
import numpy as np
import cv2
import os
import json

file_list = os.listdir("./PROP_ADAIR")

res_dict = dict()

for file in file_list[:]:
	print('./PROP_ADAIR/'+file)
	A = blueThreshold('./PROP_ADAIR/'+file, output = 'array', bin_range = 15)
	print(A)

	cv2.namedWindow('threshold', cv2.WINDOW_NORMAL)
	cv2.imshow('threshold', A)
	cv2.waitKey(0)
	cv2.destroyAllWindows()

	A2 = cv2.medianBlur(A, 5)

	center1 = manualRadCenter(A2, 300)
	print(center1)
	res_dict[file] = tuple(center1)


print(res_dict)
with open('prop_adair_radial_centers.txt', 'w') as f:
	f.write(json.dumps(res_dict, default=int))


