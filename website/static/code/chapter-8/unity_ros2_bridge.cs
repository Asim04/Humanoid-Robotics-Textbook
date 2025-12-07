/*
 * File: unity_ros2_bridge.cs
 * Purpose: Unity-ROS2 bridge for robot visualization and control
 * Chapter: 8 - Unity for Robot Visualization
 * Dependencies: Unity-ROS2-Integration package, ROS2DDS
 * Hardware: Unity simulation environment
 */

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using Unity.Robotics.ROSTCPConnector.MessageTypes.Sensor;
using Unity.Robotics.ROSTCPConnector.MessageTypes.Geometry;
using Unity.Robotics.ROSTCPConnector.MessageTypes.Nav;
using System;

public class UnityROS2Bridge : MonoBehaviour
{
    [Header("ROS2 Connection")]
    public string rosIPAddress = "127.0.0.1";
    public int rosPort = 10000;

    [Header("Robot Configuration")]
    public GameObject robotModel;
    public string robotName = "my_robot";
    public string cmdVelTopic = "/cmd_vel";
    public string odomTopic = "/odom";
    public string laserScanTopic = "/scan";

    [Header("Visualization Settings")]
    public float positionScale = 1.0f;  // Scale factor for position data
    public float rotationScale = 1.0f;  // Scale factor for rotation data

    private ROSConnection ros;
    private float updateRate = 0.1f;  // Update rate in seconds
    private float lastUpdateTime = 0f;

    // Robot state
    private Vector3 currentRobotPosition = Vector3.zero;
    private Quaternion currentRobotRotation = Quaternion.identity;
    private Vector3 currentRobotVelocity = Vector3.zero;

    void Start()
    {
        // Initialize ROS connection
        ros = ROSConnection.GetOrCreateInstance();
        ros.Initialize(rosIPAddress, rosPort);

        // Subscribe to ROS topics
        ros.Subscribe<OdometryMsg>(odomTopic, OnOdometryReceived);
        ros.Subscribe<LaserScanMsg>(laserScanTopic, OnLaserScanReceived);

        Debug.Log($"Unity-ROS2 bridge initialized. Connecting to {rosIPAddress}:{rosPort}");
        Debug.Log($"Subscribed to topics: {odomTopic}, {laserScanTopic}");
    }

    void Update()
    {
        // Update robot position and rotation in Unity based on ROS data
        if (robotModel != null)
        {
            robotModel.transform.position = currentRobotPosition * positionScale;
            robotModel.transform.rotation = currentRobotRotation * Quaternion.Euler(0, 180, 0); // Flip if needed
        }

        // Send command velocity periodically
        if (Time.time - lastUpdateTime >= updateRate)
        {
            SendCommandVelocity();
            lastUpdateTime = Time.time;
        }
    }

    void OnOdometryReceived(OdometryMsg odom)
    {
        // Convert ROS odometry data to Unity coordinates
        currentRobotPosition = new Vector3(
            odom.pose.pose.position.x,
            odom.pose.pose.position.z,  // Swap Y and Z if needed
            odom.pose.pose.position.y
        );

        // Convert quaternion from ROS to Unity (ROS uses different coordinate system)
        currentRobotRotation = new Quaternion(
            odom.pose.pose.orientation.x,
            odom.pose.pose.orientation.z,  // Swap Y and Z if needed
            odom.pose.pose.orientation.y,
            odom.pose.pose.orientation.w
        );

        // Store velocity information
        currentRobotVelocity = new Vector3(
            odom.twist.twist.linear.x,
            odom.twist.twist.linear.z,
            odom.twist.twist.linear.y
        );

        Debug.Log($"Robot position: {currentRobotPosition}, rotation: {currentRobotRotation.eulerAngles}");
    }

    void OnLaserScanReceived(LaserScanMsg scan)
    {
        // Process laser scan data for visualization
        Debug.Log($"Received laser scan: {scan.ranges.Length} points, range {scan.range_min} to {scan.range_max}");

        // You can visualize the laser scan data here
        VisualizeLaserScan(scan);
    }

    void VisualizeLaserScan(LaserScanMsg scan)
    {
        // Create visualization of laser scan data
        for (int i = 0; i < scan.ranges.Length; i += 10) // Sample every 10th point for performance
        {
            if (i < scan.ranges.Length && !float.IsNaN(scan.ranges[i]) && !float.IsInfinity(scan.ranges[i]))
            {
                float angle = scan.angle_min + i * scan.angle_increment;
                Vector3 direction = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle));
                Vector3 position = currentRobotPosition + direction * scan.ranges[i] * positionScale;

                // Visualize the laser point (you might want to create actual game objects or use debug drawing)
                Debug.DrawRay(currentRobotPosition, direction * scan.ranges[i] * positionScale, Color.red, 0.1f);
            }
        }
    }

    void SendCommandVelocity()
    {
        // Example: Send a simple command to move the robot in a circle
        float linearVel = 0.5f;  // m/s
        float angularVel = 0.2f; // rad/s

        // Create Twist message
        TwistMsg cmdVel = new TwistMsg();
        cmdVel.linear = new Vector3Msg(linearVel, 0, 0);   // Move forward
        cmdVel.angular = new Vector3Msg(0, 0, angularVel); // Rotate

        // Publish to ROS
        ros.Publish(cmdVelTopic, cmdVel);
    }

    public void SendVelocityCommand(float linearX, float angularZ)
    {
        TwistMsg cmdVel = new TwistMsg();
        cmdVel.linear = new Vector3Msg(linearX, 0, 0);
        cmdVel.angular = new Vector3Msg(0, 0, angularZ);

        ros.Publish(cmdVelTopic, cmdVel);
    }

    public void SetRobotPosition(Vector3 position)
    {
        if (robotModel != null)
        {
            robotModel.transform.position = position * positionScale;
        }
    }

    public Vector3 GetRobotPosition()
    {
        return currentRobotPosition;
    }

    public Vector3 GetRobotVelocity()
    {
        return currentRobotVelocity;
    }

    void OnDestroy()
    {
        if (ros != null)
        {
            ros.Dispose();
        }
    }
}