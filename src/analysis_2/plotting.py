#	image thresholding

import cv2
import numpy as np
from matplotlib import pyplot as plt


import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
 
fig = plt.figure()
ax = Axes3D(fig)
 
n = 33
m = 24
rad = np.linspace(0, 10, m)
a = np.linspace(0, 2 * np.pi, n)


print(a)

r, th = np.meshgrid(rad, a)
 
z = np.random.uniform(-1, 1, (n,m))
plt.subplot(projection="polar")
 
plt.pcolormesh(th, r, z, cmap = 'Blues')
 
plt.plot(a, r, ls='none', color = 'k') 
plt.grid()
plt.colorbar()
plt.show()