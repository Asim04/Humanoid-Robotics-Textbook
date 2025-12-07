#!/usr/bin/env python3
"""
File: computer_vision_example.py
Purpose: Demonstrates computer vision techniques for object detection and tracking
Chapter: 4 - Sensors and Perception
Dependencies: rclpy, sensor_msgs, cv_bridge, opencv-python
Hardware: Camera (simulation)
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
from geometry_msgs.msg import Point
from std_msgs.msg import String


class ComputerVisionNode(Node):
    """
    A node that demonstrates computer vision techniques including
    object detection, feature extraction, and tracking.
    """

    def __init__(self):
        super().__init__('computer_vision_node')

        # Initialize OpenCV bridge
        self.bridge = CvBridge()

        # Initialize tracking variables
        self.tracking_enabled = False
        self.tracking_object = None
        self.tracker = None
        self.roi = None  # Region of interest for tracking

        # Create subscriber for camera image
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Create publishers for vision results
        self.object_detection_pub = self.create_publisher(
            String,
            '/vision/object_detected',
            10
        )

        self.object_position_pub = self.create_publisher(
            Point,
            '/vision/object_position',
            10
        )

        self.feature_points_pub = self.create_publisher(
            String,
            '/vision/feature_points',
            10
        )

        self.get_logger().info('Computer vision node initialized')

    def image_callback(self, msg):
        """Process incoming image messages."""
        try:
            # Convert ROS Image message to OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

            # Apply computer vision techniques
            processed_image = self.process_image(cv_image)

            # Display the processed image
            cv2.imshow('Computer Vision Processing', processed_image)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

    def process_image(self, image):
        """Apply various computer vision techniques to the image."""
        # Create a copy of the image to draw on
        display_image = image.copy()

        # 1. Object Detection - Simple color-based detection
        object_center = self.detect_red_object(image, display_image)

        # 2. Feature Detection - Detect corners using Shi-Tomasi
        self.detect_features(image, display_image)

        # 3. Object Tracking - Initialize or update tracker
        if self.tracking_enabled and self.tracker is not None:
            self.update_tracker(image, display_image)
        else:
            # Initialize tracker on first detection of red object
            if object_center is not None and self.roi is not None:
                self.initialize_tracker(image, self.roi)
                self.tracking_enabled = True

        return display_image

    def detect_red_object(self, image, display_image):
        """Detect red objects in the image."""
        # Convert BGR to HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define range for red color
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])

        # Create masks for red color
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 + mask2

        # Apply morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        object_center = None

        if contours:
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)

            if cv2.contourArea(largest_contour) > 500:  # Filter out small contours
                # Get bounding box
                x, y, w, h = cv2.boundingRect(largest_contour)

                # Calculate center
                center_x = x + w // 2
                center_y = y + h // 2
                object_center = (center_x, center_y)

                # Draw bounding box and center
                cv2.rectangle(display_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(display_image, object_center, 5, (255, 0, 0), -1)
                cv2.putText(display_image, 'Red Object', (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Publish object detection
                detection_msg = String()
                detection_msg.data = f'Red object detected at ({center_x}, {center_y})'
                self.object_detection_pub.publish(detection_msg)

                # Publish object position
                position_msg = Point()
                position_msg.x = float(center_x)
                position_msg.y = float(center_y)
                position_msg.z = 0.0  # Depth not available from 2D image
                self.object_position_pub.publish(position_msg)

                # Store ROI for potential tracking
                self.roi = (x, y, w, h)

        return object_center

    def detect_features(self, image, display_image):
        """Detect and draw feature points in the image."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect corners using Shi-Tomasi corner detector
        corners = cv2.goodFeaturesToTrack(gray, maxCorners=50, qualityLevel=0.01, minDistance=20)

        if corners is not None:
            corners = np.int0(corners)

            # Draw corners
            for corner in corners:
                x, y = corner.ravel()
                cv2.circle(display_image, (x, y), 3, (255, 0, 0), -1)

            # Publish feature count
            features_msg = String()
            features_msg.data = f'Detected {len(corners)} features'
            self.feature_points_pub.publish(features_msg)

    def initialize_tracker(self, image, roi):
        """Initialize object tracker with ROI."""
        # Create tracker (using MOSSE tracker as it's fast)
        self.tracker = cv2.legacy.TrackerMOSSE_create()
        # Note: In newer OpenCV versions, you might need to use:
        # self.tracker = cv2.TrackerMOSSE_create()

        # Initialize tracker with ROI
        self.tracker.init(image, roi)
        self.get_logger().info(f'Tracker initialized with ROI: {roi}')

    def update_tracker(self, image, display_image):
        """Update object tracker."""
        if self.tracker is not None:
            success, bbox = self.tracker.update(image)

            if success:
                # Draw bounding box
                p1 = (int(bbox[0]), int(bbox[1]))
                p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(display_image, p1, p2, (255, 0, 0), 2)

                # Calculate center
                center_x = int(bbox[0] + bbox[2] / 2)
                center_y = int(bbox[1] + bbox[3] / 2)
                cv2.circle(display_image, (center_x, center_y), 5, (0, 0, 255), -1)

                # Publish tracking info
                tracking_msg = String()
                tracking_msg.data = f'Tracking object at ({center_x}, {center_y})'
                self.object_detection_pub.publish(tracking_msg)

                # Publish object position
                position_msg = Point()
                position_msg.x = float(center_x)
                position_msg.y = float(center_y)
                position_msg.z = 0.0
                self.object_position_pub.publish(position_msg)
            else:
                self.get_logger().warning('Tracking failed - object lost')
                self.tracking_enabled = False
                self.tracker = None


def main(args=None):
    rclpy.init(args=args)

    computer_vision_node = ComputerVisionNode()

    try:
        rclpy.spin(computer_vision_node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        computer_vision_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()