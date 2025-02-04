from btConnection import connect_via_bluetooth
from pickPoints import select_points
from homography import apply_homography_to_image
from colorMask import filter_by_color_range, average_points_of_blobs, get_farthest_point
from locateRobot import best_location
from moveRobot import calculate_relative_angle, moveRobot, move
import cv2
import numpy as np
import time
import math  # For distance and angle calculations

# Set dimensions for the images and UI components
height, width = 800, 1200
button_height = 65

homography = np.full((height, width, 3), (255, 0, 0), dtype=np.uint8)
outputImage = np.full((height, width, 3), (255, 0, 0), dtype=np.uint8)

blueImage = np.full((height, width, 3), (255, 0, 0), dtype=np.uint8)
pinkImage = np.full((height, width, 3), (255, 0, 0), dtype=np.uint8)

steps = [
    outputImage,
    homography,
    blueImage,
    pinkImage
]
names = ["Output","Perspective","Blue Mask", "Pink Mask"]

# Calculate button widths and define button areas at the bottom
button_width = width // len(steps)
button_areas = []
for i in range(len(steps)):
    x1 = i * button_width
    y1 = height
    x2 = (i + 1) * button_width
    y2 = height + button_height
    button_areas.append(((x1, y1), (x2, y2)))

# Define exit button area (top-left corner)
exit_button_area = ((0, 0), (80, 30))  # width=80, height=30 for the exit button

current_step = 0  # Start with the first image step
exit_flag = False  # Flag to signal exit

# Initialize camera and capture a frame for point selection
camera = cv2.VideoCapture(0)
time.sleep(0.1)
ret, frame = camera.read()
points = select_points(frame)

# Adjusted HSV range for blue to avoid green overlap
lower_blue = np.array([90, 100, 100])
upper_blue = np.array([130, 255, 255])

# Define HSV range for bright pink/purple; adjust as necessary
lower_pink = np.array([130, 70, 30])
upper_pink = np.array([170, 255, 200])

center = (1920/2 - 40, 1080/2 - 150)

connectBluetooth = True


# Establish Bluetooth connection if desired
if connectBluetooth:
    esp32 = connect_via_bluetooth()
else:
    esp32 = None

print("----------------------")
print("CONNECTION ESTABLISHED")
print("----------------------")
input("Press ANY to start...")

def handleLogic():
    global blueImage, pinkImage, homography, outputImage
    ret, frame = camera.read()

    # Apply homography transformation
    homography = apply_homography_to_image(points, frame)
    outputImage = homography.copy()

    # Process blue mask
    blueImage = filter_by_color_range(homography, lower_blue, upper_blue)
    bluePositions = average_points_of_blobs(blueImage, 100)
    # Draw circles at detected blue points (potential backs)
    for (bx, by) in bluePositions:
        cv2.circle(outputImage, (bx, by), radius=10, color=(0, 0, 255), thickness=-1)
        cv2.circle(blueImage, (bx, by), radius=10, color=(0, 0, 255), thickness=-1)

    # Process front (purple/pink) mask
    pinkImage = filter_by_color_range(homography, lower_pink, upper_pink)
    pinkPositions = average_points_of_blobs(pinkImage, 225)
    pinkBestPosition = best_location(pinkPositions)  # The purple/pink “front” of the robot

    if pinkBestPosition is None or bluePositions is None:
        cv2.imwrite("outputImage.jpg", outputImage)
        move("s", esp32)
        print("DEVICE OBSTRUCTED")
        return

    # If we have a valid front, draw it and compute orientation
    fx, fy = pinkBestPosition
    fx = int(fx)
    fy = int(fy)
    cv2.circle(outputImage, (fx, fy), radius=25, color=(255, 255, 255), thickness=-1)
    cv2.circle(pinkImage, (fx, fy), radius=25, color=(255, 255, 255), thickness=-1)


    # 1. Find the closest blue spot to the front
    closestBlue = min(bluePositions, key=lambda bp: math.dist(bp, (fx, fy)))
    bx, by = closestBlue
    cv2.circle(outputImage, (bx, by), radius=25, color=(100, 100, 255), thickness=-1)
    cv2.circle(blueImage, (bx, by), radius=25, color=(255, 255, 255), thickness=-1)


    if closestBlue is None:
        print("no back detected.")
        return

    targetPos = center


    dx = (int) (targetPos[0])
    dy = (int) (targetPos[1])
    moveRobot(esp32, pinkBestPosition, closestBlue, targetPos)

    cv2.circle(outputImage, (dx, dy), radius=45, color=(255, 100, 100), thickness=-1)


    # 3. Draw an arrow from the back (blue) to the front (purple/pink)
    cv2.arrowedLine(
        outputImage,
        (bx, by),  # start (back)
        (fx, fy),  # end (front)
        (0, 255, 0),  # color: green
        10,  # thickness
        tipLength=0.2
    )


def draw_ui(base_image, current_step):
    """
    Draw the current image along with the UI buttons at the bottom
    and an exit button at the top-left corner.
    """
    # Resize base_image to match UI dimensions if needed
    if base_image.shape[0] != height or base_image.shape[1] != width:
        base_image = cv2.resize(base_image, (width, height))
    
    # Create a blank image that can hold the original image plus a bar for buttons
    ui_image = np.zeros((height + button_height, width, 3), dtype=np.uint8)
    ui_image[:height, :width] = base_image

    # Draw exit button at top-left
    (ex1, ey1), (ex2, ey2) = exit_button_area
    cv2.rectangle(ui_image, (ex1, ey1), (ex2, ey2), (0, 0, 255), -1)  # Red background for exit button
    cv2.rectangle(ui_image, (ex1, ey1), (ex2, ey2), (255, 255, 255), 1)  # White border
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = "Exit"
    text_size = cv2.getTextSize(text, font, 0.5, 1)[0]
    text_x = ex1 + (ex2 - ex1 - text_size[0]) // 2
    text_y = ey1 + (ey2 - ey1 + text_size[1]) // 2
    cv2.putText(ui_image, text, (text_x, text_y), font, 0.5, (255, 255, 255), 1)

    # Draw bottom step buttons
    for idx, ((x1, y1), (x2, y2)) in enumerate(button_areas):
        # Highlight the currently selected step
        if idx == current_step:
            button_color = (0, 255, 255)  # Highlight color (yellow)
        else:
            button_color = (50, 50, 50)   # Regular button color

        # Draw button rectangle and border
        cv2.rectangle(ui_image, (x1, y1), (x2, y2), button_color, -1)
        cv2.rectangle(ui_image, (x1, y1), (x2, y2), (255, 255, 255), 1)

        # Center the text on the button
        text = names[idx]
        text_size = cv2.getTextSize(text, font, 0.6, 2)[0]
        text_x = x1 + (button_width - text_size[0]) // 2
        text_y = y1 + (button_height + text_size[1]) // 2
        cv2.putText(ui_image, text, (text_x, text_y), font, 0.6, (255, 255, 255), 2)

    return ui_image

def mouse_callback(event, x, y, flags, param):
    """
    Handle mouse click events. If a click occurs within a button area,
    update the current_step accordingly, or exit if the exit button is clicked.
    """
    global current_step, exit_flag
    if event == cv2.EVENT_LBUTTONDOWN:
        # Check if exit button was clicked
        (ex1, ey1), (ex2, ey2) = exit_button_area
        if ex1 <= x < ex2 and ey1 <= y < ey2:
            exit_flag = True
            return

        # Check bottom step buttons
        for idx, ((x1, y1), (x2, y2)) in enumerate(button_areas):
            if x1 <= x < x2 and y1 <= y < y2:
                current_step = idx
                break

# Create a window and set the mouse callback for button interaction
cv2.namedWindow("Image Process")
cv2.resizeWindow("Image Process", 1200, 800)  # Example dimensions
cv2.setMouseCallback("Image Process", mouse_callback)

while not exit_flag:
    # Draw the UI with the currently selected step image
    handleLogic()

    steps = [
        outputImage,
        homography,
        blueImage,
        pinkImage
    ]
    display = draw_ui(steps[current_step], current_step)
    cv2.imshow("Image Process", display)

    # Exit loop if ESC key is pressed or exit_flag is set via the exit button
    key = cv2.waitKey(20) & 0xFF
    if key == 27:  # ESC key
        break

cv2.destroyAllWindows()
move("s", esp32)