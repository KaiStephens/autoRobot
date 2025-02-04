import cv2

def select_points(image, scale_factor=2):

    # Scale down the image for display
    orig_height, orig_width = image.shape[:2]
    scaled_width = orig_width // scale_factor
    scaled_height = orig_height // scale_factor
    scaled_image = cv2.resize(image, (scaled_width, scaled_height))

    # List to store selected coordinates
    coordinates = []

    # Mouse callback function to handle clicks
    def on_mouse(event, x, y, flags, param):
        nonlocal coordinates
        if event == cv2.EVENT_LBUTTONDOWN and len(coordinates) < 4:
            # Convert the clicked point to original image coordinates
            orig_x = x * scale_factor
            orig_y = y * scale_factor
            coordinates.append((orig_x, orig_y))
            # Draw a red circle on the scaled image where the user clicked
            cv2.circle(scaled_image, (x, y), 10, (0, 0, 255), -1)
            cv2.imshow("Image", scaled_image)
            # If four points are selected, close the window
            if len(coordinates) == 4:
                cv2.destroyWindow("Image")

    # Set up window and mouse callback
    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", on_mouse)

    # Display the image and wait for four points to be selected
    while True:
        cv2.imshow("Image", scaled_image)
        # Break if four points have been selected
        if len(coordinates) == 4:
            break
        # Optionally, allow exit with ESC key
        if cv2.waitKey(20) & 0xFF == 27:
            print("Exiting without selecting four points.")
            break

    # Cleanup and return coordinates
    cv2.destroyAllWindows()
    return coordinates