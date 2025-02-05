# Robot Navigator with Computer Vision and Bluetooth Control

![Project Screenshot](path/to/your/photo.jpg)

This project integrates computer vision, perspective correction, and Bluetooth communication to enable a robot to autonomously navigate toward a target. It uses a live camera feed to process images, detect colored markers that represent the robot’s front and back, and calculate the required movement direction. The computed commands are then transmitted via Bluetooth to an ESP32-powered motor controller.

---

## What It Does

- **Perspective Correction:**  
  The system prompts the user to select four points in the camera frame, then applies a homography transformation to achieve a bird's-eye view of the scene.

- **Color-Based Detection:**  
  Two color filters are applied: one to detect blue regions (indicating the robot's back) and another for pink/purple areas (indicating the robot's front). The program computes the average positions of detected blobs to reliably locate these markers.

- **Robot Localization & Orientation:**  
  By comparing the positions of the front and back markers, the system calculates the robot's orientation. It then determines the relative angle toward a predefined target point (center of the view) and decides on the appropriate movement command.

- **Bluetooth Motor Control:**  
  When connected, the project communicates with an ESP32 over Bluetooth to send motor commands. This allows the robot to move forward, turn left/right, or stop based on the computed orientation and distance to the target.

- **Interactive UI:**  
  An OpenCV window displays several image views (corrected perspective, blue mask, pink mask, and the final output with overlays). A clickable interface lets you switch between these views and exit the program.

---

## Demo

Video and example of code:



---

## How It Works

1. **Camera Capture & Point Selection:**  
   The program starts by capturing an image from the camera. A user interface allows the selection of four points on the image to define the area for perspective correction.

2. **Image Processing Pipeline:**  
   - **Homography Transformation:**  
     Transforms the camera image based on user-defined points.
   - **Color Masking:**  
     Applies HSV filters to create masks for blue and pink regions.
   - **Blob Analysis:**  
     Processes the masks to determine the centroids of significant blobs representing the robot’s markers.
   - **Orientation & Movement Calculation:**  
     Computes the relative angle from the robot’s front (pink marker) to a target center, then sends appropriate movement commands.

3. **Bluetooth Communication:**  
   A dedicated module handles the Bluetooth pairing, connection, and command transmission to an ESP32 motor controller, enabling the robot to physically move.

4. **User Interface:**  
   The application overlays various processing steps onto the output image and provides on-screen buttons to toggle between different views. An exit button is also available to stop the program.

---

## Modules Overview

- **Bluetooth Connection:**  
  Handles pairing and connecting to an ESP32 device via Bluetooth, and sends motor commands based on movement calculations.

- **Point Selection & Homography:**  
  Lets users select points on the captured image to compute a homography matrix that corrects the perspective.

- **Color Filtering & Blob Detection:**  
  Applies HSV filters to isolate blue and pink markers, then averages blob positions to determine the robot's orientation.

- **Robot Localization & Control:**  
  Calculates the relative angle between the robot’s markers and the target. Based on this, it issues movement commands (forward, left, right, or stop).

- **Graphical User Interface:**  
  Uses OpenCV’s drawing functions and mouse callbacks to provide an interactive display of different processing stages.

---

This project demonstrates how combining computer vision techniques with hardware control can create a responsive and autonomous robot navigation system. Check out the demo video and screenshot above for a closer look at its capabilities!

*Note: This README focuses on showcasing the features and functionality of the project. For further details on how each component works, please refer to the code comments and module documentation within the repository.*
