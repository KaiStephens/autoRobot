import cv2
import numpy as np

def apply_homography_to_image(point_list, image):
    # Determine image dimensions from the OpenCV image (NumPy array)
    height, width = image.shape[:2]

    # Use the OpenCV image directly; optionally copy if you want to preserve the original
    image_np = image.copy()

    # Convert list of points to a NumPy array of type float32
    src_points = np.array(point_list, dtype=np.float32)

    # Define destination points corresponding to the corners of the output image
    dst_points = np.array([
        [0, 0],            # Top-left corner of destination
        [width, 0],        # Top-right corner of destination
        [width, height],   # Bottom-right corner of destination
        [0, height]        # Bottom-left corner of destination
    ], dtype=np.float32)

    # Compute the homography matrix from source points to destination points
    H, _ = cv2.findHomography(src_points, dst_points)

    # Define the output image size
    output_size = (width, height)

    # Apply the homography transformation to the entire image
    warped_image = cv2.warpPerspective(image_np, H, output_size)

    return warped_image
