"""
Radial Root System Polar Plotting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_radial_density(df: pd.DataFrame, out_path:str) -> None:
    """_summary_

    Args:
        file_path (str): The path to the radial density csv file
        out_path (str): The path to save the plot at
    """

    # Convert angles to radians for polar plotting and convert radii to cm
    df['angle_rad'] = np.deg2rad(df['angle'])
    df['radius_norm'] = df['radius'] / 46.43333333333333333

    # Create a grid of angles and radii
    angles = np.unique(df['angle_rad'])
    radii = np.rint(np.unique(df['radius_norm'])).astype(int)
    density = df.pivot(index='radius', columns='angle_rad', values='density').values


    # Create a polar projection plot
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})

    # Create a mesh grid
    angle_grid, radius_grid = np.meshgrid(angles, radii)
    c = ax.pcolormesh(angle_grid, radius_grid, density, cmap='bone_r', shading='auto')

    # Colorbar for density measurements
    cbar = plt.colorbar(c, ax=ax, pad=0.1)
    cbar.set_label('Root Density')

    # Set plot limits and labels
    ax.set_ylim(0, 30)  # Maximum is 30cm
    # ax.set_title("Polar Plot of Density by Angle and Radius", va='bottom')
    

    # Change the y-axis (radii) tick labels to white
    ax.tick_params(axis='y', colors='white')  # Change the tick color
    for label in ax.get_yticklabels():
        label.set_color('green')
        label.set_fontweight('bold')
        label.set_fontsize(15)  # Change text color to white
    print(out_path)
    plt.savefig(out_path)
    plt.close()