import pandas as pd

from threshold import blueThreshold, manualThreshold
import cv2
from glob import glob
import os
from tqdm.auto import tqdm
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from numpy import dot, arccos, clip
from numpy.linalg import norm
from calc import unitVectors, polyPoints, getRings, getSlices, get_radial_masks

# Set directories
adair_radial_root = './data/root_crown_images/radial_images/PROP_ADAIR/'
picos_radial_root = './data/root_crown_images/radial_images/PROP_PICOS/'

adair_output = './data/output/PROP_ADAIR/'
picos_output = './data/output/PROP_PICOS/'
results_output = './data/output/results/'

for path in [adair_output, picos_output, results_output]:
    if not os.path.exists(path):
        os.makedirs(path)

# Set variables
cropDst = 1393 # 30cm from center of tree
cnt_threshold = 50
img_shape = (3456, 5184)
n_rings = 30
n_slices = 90
radii = list(np.rint([i*cropDst/n_rings for i in range(1, n_rings+1)]).astype(int))

# Precompute radial masks
vecs = unitVectors(n_slices)


adair_file_list = glob('*.JPG', root_dir=adair_radial_root)
picos_file_list = glob('*.JPG', root_dir=picos_radial_root)

radial_results_file_list = glob('*radial_density.csv', root_dir=results_output)

# Set up results files
image_results = pd.DataFrame(columns=['image_name',
                                      'center_x',
                                      'center_y',
                                      'radius',
                                      'convex_hull_area',
                                      'root_area',
                                      'solidity',
                                      'center_offset',
                                      'variance_PC1',
                                      'variance_PC2',
                                      'angle_PC1'
                                      ]
                             )

# Lambda functions
flip = lambda x: img_shape[0] - x
combined_file_list = [adair_file_list, picos_file_list]
for file_list in combined_file_list:
    if file_list == adair_file_list:
        output_dir = adair_output
        image_dir = adair_radial_root
    elif file_list == picos_file_list:
        output_dir = picos_output
        image_dir = picos_radial_root
    for i, file in enumerate(file_list):
        print(file)
        img = cv2.imread(os.path.join(image_dir, file))
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        fimg = cv2.inRange(hsv_img, (0, 0, 0), (95, 255, 255))
        cv2.imwrite(os.path.join(output_dir, f"{file[:-4]}_binary.JPG"), fimg)

        blurred = cv2.GaussianBlur(fimg, (3, 3), 1, 1)
        cv2.imwrite(os.path.join(output_dir, f"{file[:-4]}_blurred.JPG"), blurred)

        # Limit scope of Hough circles search
        zero_mask = np.zeros(fimg.shape, dtype=np.uint8)
        center_circle = cv2.circle(zero_mask, (int(zero_mask.shape[1]//2), int(zero_mask.shape[0]//2)), 100, 255, -1)
        center_mask_img = cv2.bitwise_and(blurred, blurred, mask=center_circle)
        cv2.imwrite(os.path.join(output_dir, f"{file[:-4]}_center.JPG"), center_mask_img)

        # Iterate through sensitivity params, param for filtering the "perfectness" of the circle
        # Smaller i = less perfect circles accepted
        for i in [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, .99]:
            circles = cv2.HoughCircles(center_mask_img, cv2.HOUGH_GRADIENT_ALT, 3, minDist=300, param1=300, param2=i,
                                       minRadius=5, maxRadius=45)
            src = cv2.imread(os.path.join(image_dir, file))
            if len(circles) == 1:
                for circle in circles[0]:
                    center_x, center_y, radius = circle
                    cv2.circle(src, (int(center_x), int(center_y)), int(radius), (0, 255,), 2)
                    cv2.circle(src, (int(center_x), int(center_y)), 1, (0, 0, 255), 2)
                    cv2.imwrite(os.path.join(output_dir, f"{file[:-4]}_centerdot.JPG"), src)
                    results = {'image_name': file, 'center_x': center_x, 'center_y': center_y, 'radius': radius}
                break
            elif circles is None:
                print("No circles found for ", file)
                center = {'image_name': file, 'center_x': NULL, 'center_y': NULL, 'radius': NULL}

        # Crop root system to cropDst
        center_point = (int(center_x), int(center_y))
        crop_mask = np.zeros(fimg.shape, dtype=np.uint8)
        cv2.circle(crop_mask, (int(center_x), int(center_y)), cropDst, 255, -1)
        cropped = cv2.bitwise_and(fimg, fimg, mask=crop_mask)
        cv2.imwrite(os.path.join(output_dir, f"{file[:-4]}_cropped.JPG"), cropped)
        contours, _ = cv2.findContours(cropped, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Calculate convex hull
        filtered_cnts = [cnt for cnt in contours if cv2.contourArea(cnt) >= cnt_threshold]
        hull = []
        filtered_cnts = np.concatenate(filtered_cnts)
        hull_i = cv2.convexHull(filtered_cnts, False)
        hull.append(hull_i)
        hull_area = cv2.contourArea(hull[0])

        # Mask points not within convex hull
        hull_img = cropped.copy()
        hull_mask = np.zeros(fimg.shape, np.uint8)
        hull_mask = cv2.drawContours(hull_mask, hull, -1, 255, -1)
        hull_img = cv2.bitwise_and(hull_img, hull_img, mask=hull_mask)
        root_area = np.sum(hull_img)/255 + (np.pi*(radius**2))

        cv2.drawContours(hull_img, hull, -1, 200, 4)
        cv2.imwrite(os.path.join(output_dir, f"{file[:-4]}_convexhull.JPG"), hull_img)
        results['convex_hull_area'] = hull_area
        results['root_area'] = root_area
        results['solidity'] = root_area/hull_area

        # Radial density measurements
        if f"{file[:-4]}_radial_density.csv" not in radial_results_file_list:
            poly_points, angles = polyPoints(vecs, cropDst, center_point)
            rings = getRings(radii, img_shape, center_point)
            slices = getSlices(poly_points, img_shape)
            masked_slices = get_radial_masks(rings, slices, img_shape)

            n_masks = len(rings)*len(slices)
            # pbar = tqdm([i for i in range(n_masks)])
            radial_results = pd.DataFrame(columns=["image_name", "radius", "angle", "density"])
            # for mask in pbar:
            for _ in tqdm(range(n_masks)):
                # pbar.set_description(f"Processing radial mask {mask} for {file}")
                radial_mask, (i, j) = next(masked_slices)
                # print(radial_mask.shape, indices)
                mask_area = np.sum(radial_mask)
                # print(fimg.shape, radial_mask.shape)
                masked_roots = cv2.bitwise_and(fimg, fimg, mask=radial_mask)

                root_area = np.sum(masked_roots)
                density = root_area/mask_area
                res = {"image_name": file, "radius": radii[i], "angle": angles[j], "density": density}
                radial_results = pd.concat([radial_results, pd.DataFrame(res, index=[0])], ignore_index=True)

            radial_results.to_csv(os.path.join(results_output, f"{file[:-4]}_radial_density.csv"))

        # PCA decomp of binary images for symmetry
        scaler = StandardScaler()

        # Grab coordinates of root pixels in cropped, invert, and scale
        xy_coords = np.where(cropped > 0)
        xy_coords = [i[:, np.newaxis] for i in xy_coords]
        xy_coords.reverse()
        xy_coords[1] = np.array(list(map(flip, xy_coords[1])))
        xy_coords = np.concatenate(xy_coords, axis=1)
        xy_scaled = scaler.fit_transform(xy_coords)

        # Grab center point from the image and scale
        flipped_center = list(center_point)
        flipped_center[1] = img_shape[0] - center_point[1]
        # print(center_point, flipped_center)
        flipped_center = np.array([flipped_center])
        scaled_center = scaler.transform(flipped_center)

        # Instantiate pca and fit to the scaled data
        pca = PCA()
        pca.fit_transform(xy_coords)
        offset = np.linalg.norm(scaled_center)

        # Angle between excavation and PC1
        exc_vec = np.array([1, 0])
        cos_theta = dot(np.abs(pca.components_[0]), exc_vec)
        angle = arccos(cos_theta)
        angle = np.degrees(np.array(angle))
        print(f"Angle: {angle}")


        print(f"Offset: {offset}")
        print(f"Explained Variance: {pca.explained_variance_ratio_}")
        print(f"PC: {pca.components_}")

        results['center_offset'] = offset
        results['variance_PC1'] = pca.explained_variance_ratio_[0]
        results['variance_PC2'] = pca.explained_variance_ratio_[1]
        results['angle_PC1'] = angle

        image_results = pd.concat([image_results, pd.DataFrame(results, index=[0])], ignore_index=True)



    image_results.to_csv(os.path.join(results_output, "prop_adair_image_results.csv"))
