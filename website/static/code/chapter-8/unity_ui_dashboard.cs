/*
 * File: unity_ui_dashboard.cs
 * Purpose: Unity UI dashboard for displaying ROS2 robot status and sensor data
 * Chapter: 8 - Unity for Robot Visualization
 * Dependencies: Unity-ROS2-Integration package, Unity UI system
 * Hardware: Unity simulation environment
 */

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using Unity.Robotics.ROSTCPConnector;
using Unity.Robotics.ROSTCPConnector.MessageTypes.Sensor;
using Unity.Robotics.ROSTCPConnector.MessageTypes.Geometry;
using Unity.Robotics.ROSTCPConnector.MessageTypes.Nav;
using Unity.Robotics.ROSTCPConnector.MessageTypes.Std;
using TMPro; // Using TextMeshPro for better text rendering

public class UnityUIDashboard : MonoBehaviour
{
    [Header("ROS2 Topics")]
    public string batteryTopic = "/battery_status";
    public string statusTopic = "/robot_status";
    public string diagnosticTopic = "/diagnostics";
    public string odomTopic = "/odom";
    public string imuTopic = "/imu/data";

    [Header("UI References")]
    public TextMeshProUGUI positionText;
    public TextMeshProUGUI batteryText;
    public TextMeshProUGUI statusText;
    public TextMeshProUGUI velocityText;
    public TextMeshProUGUI imuText;
    public Slider batterySlider;
    public Image batteryFill;
    public Color batteryGoodColor = Color.green;
    public Color batteryWarningColor = Color.yellow;
    public Color batteryCriticalColor = Color.red;

    [Header("Performance Settings")]
    public float updateRate = 0.5f;  // Update UI every 0.5 seconds

    private ROSConnection ros;
    private float lastUpdateTime = 0f;

    // Robot state variables
    private Vector3 currentPosition = Vector3.zero;
    private Vector3 currentVelocity = Vector3.zero;
    private float batteryLevel = 100f;
    private string robotStatus = "Unknown";
    private Vector3 imuAngularVelocity = Vector3.zero;
    private Vector3 imuLinearAcceleration = Vector3.zero;

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();

        // Subscribe to ROS topics
        ros.Subscribe<OdometryMsg>(odomTopic, OnOdometryReceived);
        ros.Subscribe<ImuMsg>(imuTopic, OnImuReceived);
        // Note: Battery and status topics would need to be implemented based on your specific robot

        Debug.Log($"Unity UI dashboard initialized. Subscribed to: {odomTopic}, {imuTopic}");

        // Initialize UI with default values
        UpdateUI();
    }

    void Update()
    {
        // Update UI at specified rate
        if (Time.time - lastUpdateTime >= updateRate)
        {
            UpdateUI();
            lastUpdateTime = Time.time;
        }
    }

    void OnOdometryReceived(OdometryMsg odom)
    {
        // Update position
        currentPosition = new Vector3(
            (float)odom.pose.pose.position.x,
            (float)odom.pose.pose.position.z,  // Swap Y and Z if needed
            (float)odom.pose.pose.position.y
        );

        // Update velocity
        currentVelocity = new Vector3(
            (float)odom.twist.twist.linear.x,
            (float)odom.twist.twist.linear.z,
            (float)odom.twist.twist.linear.y
        );
    }

    void OnImuReceived(ImuMsg imu)
    {
        // Update IMU data
        imuAngularVelocity = new Vector3(
            (float)imu.angular_velocity.x,
            (float)imu.angular_velocity.y,
            (float)imu.angular_velocity.z
        );

        imuLinearAcceleration = new Vector3(
            (float)imu.linear_acceleration.x,
            (float)imu.linear_acceleration.y,
            (float)imu.linear_acceleration.z
        );
    }

    void UpdateUI()
    {
        // Update position display
        if (positionText != null)
        {
            positionText.text = $"Position: X:{currentPosition.x:F2} Y:{currentPosition.y:F2} Z:{currentPosition.z:F2}";
        }

        // Update velocity display
        if (velocityText != null)
        {
            float speed = currentVelocity.magnitude;
            velocityText.text = $"Velocity: {speed:F2} m/s (X:{currentVelocity.x:F2} Y:{currentVelocity.y:F2} Z:{currentVelocity.z:F2})";
        }

        // Update IMU display
        if (imuText != null)
        {
            imuText.text = $"IMU: Ang.Vel({imuAngularVelocity.x:F2}, {imuAngularVelocity.y:F2}, {imuAngularVelocity.z:F2}) " +
                          $"Lin.Accel({imuLinearAcceleration.x:F2}, {imuLinearAcceleration.y:F2}, {imuLinearAcceleration.z:F2})";
        }

        // Update battery display (simulated)
        if (batteryText != null)
        {
            batteryText.text = $"Battery: {batteryLevel:F1}%";
        }

        // Update battery slider
        if (batterySlider != null)
        {
            batterySlider.value = batteryLevel / 100f;
        }

        // Update battery fill color based on level
        if (batteryFill != null)
        {
            Color batteryColor = GetBatteryColor(batteryLevel / 100f);
            batteryFill.color = batteryColor;
        }

        // Update status display
        if (statusText != null)
        {
            statusText.text = $"Status: {robotStatus}";
        }
    }

    Color GetBatteryColor(float batteryLevel)
    {
        if (batteryLevel > 0.5f)
        {
            // Good level - interpolate between green and yellow
            return Color.Lerp(batteryGoodColor, batteryWarningColor, (batteryLevel - 0.5f) * 2f);
        }
        else
        {
            // Warning/Critical level - interpolate between yellow and red
            return Color.Lerp(batteryWarningColor, batteryCriticalColor, (0.5f - batteryLevel) * 2f);
        }
    }

    // Public methods for external control
    public void SetBatteryLevel(float level)
    {
        batteryLevel = Mathf.Clamp(level, 0f, 100f);
    }

    public void SetRobotStatus(string status)
    {
        robotStatus = status;
    }

    public void SetPosition(Vector3 position)
    {
        currentPosition = position;
    }

    public void SetVelocity(Vector3 velocity)
    {
        currentVelocity = velocity;
    }

    public Vector3 GetPosition()
    {
        return currentPosition;
    }

    public Vector3 GetVelocity()
    {
        return currentVelocity;
    }

    public float GetBatteryLevel()
    {
        return batteryLevel;
    }

    public string GetRobotStatus()
    {
        return robotStatus;
    }

    // Method to handle emergency stop
    public void EmergencyStop()
    {
        // Publish emergency stop command to ROS
        if (ros != null)
        {
            var cmdVel = new TwistMsg();
            cmdVel.linear = new Vector3Msg(0, 0, 0);
            cmdVel.angular = new Vector3Msg(0, 0, 0);

            ros.Publish("/cmd_vel", cmdVel);
            SetRobotStatus("Emergency Stop Activated");

            Debug.Log("Emergency stop command sent to robot");
        }
    }

    // Method to reset robot status
    public void ResetStatus()
    {
        SetRobotStatus("Operational");
    }

    // Method to update multiple UI elements at once
    public void UpdateRobotData(Vector3 position, Vector3 velocity, float battery, string status)
    {
        SetPosition(position);
        SetVelocity(velocity);
        SetBatteryLevel(battery);
        SetRobotStatus(status);
    }

    void OnDestroy()
    {
        if (ros != null)
        {
            ros.Dispose();
        }
    }
}