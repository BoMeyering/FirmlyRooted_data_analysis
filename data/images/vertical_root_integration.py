import sys
sys.path.insert(0, '../../../../github_repos/tria/src/tria/')

from calc import getIntegralDepth
import pandas as pd
import cv2
import matplotlib.pyplot as plt
import os

adair_list = os.listdir('prop_adair_threshold_cropped')
res = []
# print(adair_list)
for file in adair_list:
	#print(file)
	A = cv2.imread('prop_adair_threshold_cropped/'+file, cv2.IMREAD_UNCHANGED)
	res.append(getIntegralDepth(A))

df_adair = pd.DataFrame({"filename": adair_list, "pixel_depth": res})

picos_list = os.listdir('prop_picos_threshold_cropped')
res = []
# print(picos_list)
for file in picos_list:
	A = cv2.imread('prop_picos_threshold_cropped/'+file, cv2.IMREAD_UNCHANGED)
	res.append(getIntegralDepth(A))

df_picos = pd.DataFrame({'filename': picos_list, 'pixel_depth': res})

df_adair.to_csv('prop_adair_pixel_depths.csv')
df_picos.to_csv('prop_picos_pixel_depths.csv')


