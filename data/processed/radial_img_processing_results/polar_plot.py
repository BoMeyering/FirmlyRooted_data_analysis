import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Read in in the data
df = pd.read_csv('47_58_0_radial_density.csv')

# Convert angles to radians for polar plotting
df['angle_rad'] = np.deg2rad(df['angle'])

# Normalize radii for better visualization (optional, based on data scale)
df['radius_norm'] = df['radius'] / df['radius'].max()
df['radius_norm'] = df['radius'] / 46.43333333333333333

# Create a grid of angles and radii
angles = np.unique(df['angle_rad'])
radii = np.rint(np.unique(df['radius_norm'])).astype(int)
print(radii)
density = df.pivot(index='radius', columns='angle_rad', values='density').values
print(density)

# Create a polar plot
fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': 'polar'})

# Use pcolormesh to create a filled polar plot
angle_grid, radius_grid = np.meshgrid(angles, radii)

# print(angle_grid)
# print(radius_grid)
c = ax.pcolormesh(angle_grid, radius_grid, density, cmap='bone_r', shading='auto')
# print(c)

# Add a color bar to show density values
cbar = plt.colorbar(c, ax=ax, pad=0.1)
cbar.set_label('Density')

# Set plot limits and labels
ax.set_ylim(0, 30)  # Adjust based on normalized radii
# ax.set_title("Polar Plot of Density by Angle and Radius", va='bottom')

plt.text(10, 10, 'matplotlib')

# Change the y-axis (radii) tick labels to white
ax.tick_params(axis='y', colors='white')  # Change the tick color
for label in ax.get_yticklabels():
    label.set_color('green')
    label.set_fontweight('bold')
    label.set_fontsize(15)  # Change text color to white

plt.savefig('test.PNG')
plt.show()
