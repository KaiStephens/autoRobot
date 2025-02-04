import cv2
import numpy as np

def filter_by_color_range(image, lower_bound, upper_bound):
    # Convert the input image from BGR to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Create a mask for the specified HSV range
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    
    # Apply the mask to the original image
    result = cv2.bitwise_and(image, image, mask=mask)
    
    return result

def average_points_of_blobs(filtered_image, min_size):
    # Convert the filtered image to grayscale
    gray = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2GRAY)
    
    # Create a binary mask where non-black pixels (i.e., within the color range) are white
    _, binary_mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    
    # Perform connected components analysis
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_mask, connectivity=8)
    
    valid_centroids = []
    # Skip the first label (background)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        # Only consider blobs meeting the minimum size requirement
        if area >= min_size:
            # Centroids are returned as float coordinates; convert them if desired
            centroid = (int(centroids[i][0]), int(centroids[i][1]))
            valid_centroids.append(centroid)
    
    return valid_centroids

def get_farthest_point(image):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold to get a binary mask
    _, binaryBlue = cv2.threshold(image, 1, 255, cv2.THRESH_BINARY)

    # Invert it
    invertedMask = cv2.bitwise_not(binaryBlue)

    # Ensure it's CV_8UC1
    invertedMask = invertedMask.astype(np.uint8)

    # Now apply the distance transform
    distTransform = cv2.distanceTransform(invertedMask, cv2.DIST_L2, 3)

    # Find the max location
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(distTransform)
    farthest_point = maxLoc

    # 5. (Optional) visualize that point on the homography-corrected image
    return farthest_point