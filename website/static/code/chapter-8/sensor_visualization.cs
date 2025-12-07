/*
 * File: sensor_visualization.cs
 * Purpose: Unity script for visualizing ROS2 sensor data (LiDAR, camera, IMU)
 * Chapter: 8 - Unity for Robot Visualization
 * Dependencies: Unity-ROS2-Integration package
 * Hardware: Unity simulation environment
 */

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using Unity.Robotics.ROSTCPConnector.MessageTypes.Sensor;
using Unity.Robotics.ROSTCPConnector.MessageTypes.Geometry;
using Unity.Robotics.ROSTCPConnector.MessageTypes.Std;
using System;

public class SensorVisualization : MonoBehaviour
{
    [Header("Sensor Topics")]
    public string laserScanTopic = "/scan";
    public string pointCloudTopic = "/pointcloud";
    public string imuTopic = "/imu/data";
    public string cameraInfoTopic = "/camera_info";
    public string imageTopic = "/image_raw";

    [Header("Visualization Settings")]
    public GameObject laserPointPrefab;
    public Material laserMaterial;
    public Color laserColor = Color.red;
    public float laserPointSize = 0.05f;
    public int maxLaserPoints = 1000;

    [Header("Performance Settings")]
    public float updateRate = 0.1f;
    public bool enableRealTimeVisualization = true;

    private ROSConnection ros;
    private List<GameObject> laserPoints = new List<GameObject>();
    private float lastUpdateTime = 0f;

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();

        // Subscribe to sensor topics
        ros.Subscribe<LaserScanMsg>(laserScanTopic, OnLaserScanReceived);
        ros.Subscribe<PointCloud2Msg>(pointCloudTopic, OnPointCloudReceived);
        ros.Subscribe<ImuMsg>(imuTopic, OnImuReceived);

        Debug.Log($"Sensor visualization initialized. Subscribed to: {laserScanTopic}, {pointCloudTopic}, {imuTopic}");
    }

    void Update()
    {
        if (enableRealTimeVisualization && Time.time - lastUpdateTime >= updateRate)
        {
            lastUpdateTime = Time.time;
        }
    }

    void OnLaserScanReceived(LaserScanMsg scan)
    {
        Debug.Log($"Received laser scan with {scan.ranges.Length} points");

        // Clear previous laser points
        ClearLaserPoints();

        // Create new laser points based on scan data
        if (laserPointPrefab != null)
        {
            CreateLaserPointsFromScan(scan);
        }
        else
        {
            // Alternative: use debug visualization
            VisualizeLaserScanWithDebug(scan);
        }
    }

    void OnPointCloudReceived(PointCloud2Msg pointCloud)
    {
        Debug.Log($"Received point cloud with {pointCloud.height * pointCloud.width} points");

        // Process point cloud data
        ProcessPointCloud(pointCloud);
    }

    void OnImuReceived(ImuMsg imu)
    {
        Debug.Log($"Received IMU data: angular velocity ({imu.angular_velocity.x}, {imu.angular_velocity.y}, {imu.angular_velocity.z}), " +
                  $"linear acceleration ({imu.linear_acceleration.x}, {imu.linear_acceleration.y}, {imu.linear_acceleration.z})");

        // Visualize IMU data (e.g., as a 3D orientation indicator)
        VisualizeImuData(imu);
    }

    void CreateLaserPointsFromScan(LaserScanMsg scan)
    {
        // Limit the number of points for performance
        int stepSize = Mathf.Max(1, scan.ranges.Length / maxLaserPoints);

        for (int i = 0; i < scan.ranges.Length; i += stepSize)
        {
            if (i < scan.ranges.Length &&
                !float.IsNaN(scan.ranges[i]) &&
                !float.IsInfinity(scan.ranges[i]) &&
                scan.ranges[i] >= scan.range_min &&
                scan.ranges[i] <= scan.range_max)
            {
                float angle = scan.angle_min + i * scan.angle_increment;
                Vector3 direction = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle));
                Vector3 worldPosition = transform.position + direction * scan.ranges[i];

                GameObject point = Instantiate(laserPointPrefab, worldPosition, Quaternion.identity);
                point.transform.localScale = Vector3.one * laserPointSize;

                if (laserMaterial != null)
                {
                    Renderer renderer = point.GetComponent<Renderer>();
                    if (renderer != null)
                    {
                        renderer.material = laserMaterial;
                    }
                }

                laserPoints.Add(point);
            }
        }
    }

    void VisualizeLaserScanWithDebug(LaserScanMsg scan)
    {
        // Use Unity's debug visualization for laser points
        for (int i = 0; i < scan.ranges.Length; i += 10) // Sample every 10th point
        {
            if (i < scan.ranges.Length &&
                !float.IsNaN(scan.ranges[i]) &&
                !float.IsInfinity(scan.ranges[i]) &&
                scan.ranges[i] >= scan.range_min &&
                scan.ranges[i] <= scan.range_max)
            {
                float angle = scan.angle_min + i * scan.angle_increment;
                Vector3 direction = new Vector3(Mathf.Cos(angle), 0, Mathf.Sin(angle));
                Vector3 worldPosition = transform.position + direction * scan.ranges[i];

                Debug.DrawRay(transform.position, direction * scan.ranges[i], laserColor, 0.1f);
            }
        }
    }

    void ProcessPointCloud(PointCloud2Msg pointCloud)
    {
        // Note: Processing PointCloud2 requires parsing binary data
        // This is a simplified example - in practice, you'd need to parse the binary data according to the fields
        Debug.Log($"Processing point cloud: {pointCloud.height}x{pointCloud.width} points");

        // For now, just log the structure
        Debug.Log($"Point cloud fields: {pointCloud.fields.Count}");
        foreach (var field in pointCloud.fields)
        {
            Debug.Log($"  Field: {field.name}, offset: {field.offset}, datatype: {field.datatype}, count: {field.count}");
        }
    }

    void VisualizeImuData(ImuMsg imu)
    {
        // Create a visual representation of the IMU orientation
        // Convert quaternion to Unity coordinate system if needed
        Quaternion imuRotation = new Quaternion(
            imu.orientation.x,
            imu.orientation.y,
            imu.orientation.z,
            imu.orientation.w
        );

        // Apply the rotation to a visual indicator (e.g., a small 3D model)
        transform.rotation = imuRotation;

        // You could also visualize the angular velocity and linear acceleration as vectors
        Vector3 angularVel = new Vector3(
            (float)imu.angular_velocity.x,
            (float)imu.angular_velocity.y,
            (float)imu.angular_velocity.z
        ) * 10f; // Scale for visibility

        Vector3 linearAccel = new Vector3(
            (float)imu.linear_acceleration.x,
            (float)imu.linear_acceleration.y,
            (float)imu.linear_acceleration.z
        ) * 10f; // Scale for visibility

        Debug.DrawRay(transform.position, angularVel, Color.blue, 0.1f);
        Debug.DrawRay(transform.position, linearAccel, Color.green, 0.1f);
    }

    void ClearLaserPoints()
    {
        foreach (GameObject point in laserPoints)
        {
            if (point != null)
            {
                DestroyImmediate(point);
            }
        }
        laserPoints.Clear();
    }

    // Public methods for external control
    public void SetLaserVisualizationEnabled(bool enabled)
    {
        enableRealTimeVisualization = enabled;
        if (!enabled)
        {
            ClearLaserPoints();
        }
    }

    public void SetMaxLaserPoints(int maxPoints)
    {
        maxLaserPoints = maxPoints;
    }

    public void SetLaserPointSize(float size)
    {
        laserPointSize = size;
        // Update existing points if needed
        foreach (GameObject point in laserPoints)
        {
            if (point != null)
            {
                point.transform.localScale = Vector3.one * size;
            }
        }
    }

    void OnDestroy()
    {
        ClearLaserPoints();
    }
}