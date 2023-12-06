import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import cv2

img = cv2.imread('30E_0_binary.JPG', cv2.IMREAD_UNCHANGED)
h = img.shape[0]
print(img)

flip = lambda x: h - x

scaler = StandardScaler()
xy_coords = np.where(img>0)
xy_coords = [i[:, np.newaxis] for i in xy_coords]
xy_coords.reverse()

xy_coords[1] = np.array(list(map(flip, xy_coords[1])))

xy_coords = np.concatenate(xy_coords, axis = 1)

xy_scaled = scaler.fit_transform(xy_coords)

import matplotlib.pyplot as plt

# center_point = np.array([2634, 1734]) # 15e
# center_point = np.array([2604, 1713]) # 55e
center_point = np.array([[2610, 1710]]) # 30e

scaled_center = scaler.transform(center_point)
print(f"Center Point: {center_point}")
print(f"Scaled Center: {scaled_center}")
print(f"Scaled Offset: {np.linalg.norm(scaled_center)}")

pca = PCA()
pca.fit_transform(xy_coords)
# print(pca.components_)
# print(pca.explained_variance_)
print(pca.explained_variance_ratio_)
print(pca.mean_)
new_center = center_point - pca.mean_
print(new_center)
dist = np.linalg.norm(center_point - pca.mean_)
print(f"Unormalized Distance: {dist}")

plt.scatter(xy_scaled[:, 0], xy_scaled[:, 1], s = .2)
plt.show()
