/*
 * File: robot_animation_controller.cs
 * Purpose: Unity script for controlling robot model animation based on ROS2 joint states
 * Chapter: 8 - Unity for Robot Visualization
 * Dependencies: Unity-ROS2-Integration package, JointState messages
 * Hardware: Unity simulation environment
 */

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using Unity.Robotics.ROSTCPConnector;
using Unity.Robotics.ROSTCPConnector.MessageTypes.Sensor;
using Unity.Robotics.ROSTCPConnector.MessageTypes.Geometry;
using System.Linq;

public class RobotAnimationController : MonoBehaviour
{
    [Header("ROS2 Configuration")]
    public string jointStateTopic = "/joint_states";
    public string robotDescriptionTopic = "/robot_description";

    [Header("Joint Configuration")]
    public JointConfig[] jointConfigs;

    [Header("Performance Settings")]
    public float animationSmoothness = 0.1f;  // Lower values = smoother but less responsive
    public bool enableJointInterpolation = true;

    private ROSConnection ros;
    private Dictionary<string, JointStateData> jointStates = new Dictionary<string, JointStateData>();
    private Dictionary<string, Transform> jointTransforms = new Dictionary<string, Transform>();

    [System.Serializable]
    public class JointConfig
    {
        public string jointName;
        public string jointTransformPath;  // Path to the joint transform in the hierarchy
        public JointType jointType = JointType.Revolute;
        public float minAngle = -180f;
        public float maxAngle = 180f;
        public float minPosition = -1f;
        public float maxPosition = 1f;
        public Vector3 rotationAxis = Vector3.up;
        public Vector3 positionAxis = Vector3.forward;
    }

    public enum JointType
    {
        Revolute,    // Rotational joint
        Continuous,  // Continuous rotational joint
        Prismatic,   // Linear joint
        Fixed        // Fixed joint (no movement)
    }

    [System.Serializable]
    public class JointStateData
    {
        public float position = 0f;
        public float velocity = 0f;
        public float effort = 0f;
        public float targetPosition = 0f;
        public float lastUpdateTime = 0f;
    }

    void Start()
    {
        ros = ROSConnection.GetOrCreateInstance();

        // Subscribe to joint states
        ros.Subscribe<JointStateMsg>(jointStateTopic, OnJointStateReceived);

        // Initialize joint transforms
        InitializeJointTransforms();

        Debug.Log($"Robot animation controller initialized. Subscribed to: {jointStateTopic}");
    }

    void InitializeJointTransforms()
    {
        // Find all joint transforms based on the configuration
        foreach (JointConfig config in jointConfigs)
        {
            Transform jointTransform = null;

            // Try to find the joint transform by path
            if (!string.IsNullOrEmpty(config.jointTransformPath))
            {
                jointTransform = transform.Find(config.jointTransformPath);
            }

            if (jointTransform != null)
            {
                jointTransforms[config.jointName] = jointTransform;
                jointStates[config.jointName] = new JointStateData();
                Debug.Log($"Found joint '{config.jointName}' at path '{config.jointTransformPath}'");
            }
            else
            {
                Debug.LogWarning($"Could not find joint transform for '{config.jointName}' at path '{config.jointTransformPath}'");
            }
        }
    }

    void Update()
    {
        // Update joint animations
        UpdateJointAnimations();
    }

    void OnJointStateReceived(JointStateMsg jointState)
    {
        // Process each joint in the received message
        for (int i = 0; i < jointState.name.Count; i++)
        {
            string jointName = jointState.name[i];
            float position = (float)jointState.position[i];

            // Check if this joint is configured for this robot
            if (jointStates.ContainsKey(jointName))
            {
                JointStateData jointData = jointStates[jointName];
                jointData.targetPosition = position;
                jointData.lastUpdateTime = Time.time;

                // Also store velocity and effort if available
                if (i < jointState.velocity.Count)
                {
                    jointData.velocity = (float)jointState.velocity[i];
                }
                if (i < jointState.effort.Count)
                {
                    jointData.effort = (float)jointState.effort[i];
                }
            }
        }
    }

    void UpdateJointAnimations()
    {
        foreach (var jointPair in jointStates)
        {
            string jointName = jointPair.Key;
            JointStateData jointData = jointPair.Value;

            if (jointTransforms.ContainsKey(jointName))
            {
                JointConfig config = GetJointConfig(jointName);
                if (config != null)
                {
                    Transform jointTransform = jointTransforms[jointName];

                    // Calculate current position based on interpolation setting
                    float currentPosition;
                    if (enableJointInterpolation)
                    {
                        // Smoothly interpolate to target position
                        float smoothedPosition = Mathf.Lerp(jointData.position, jointData.targetPosition,
                                                          Mathf.Clamp01(Time.deltaTime / animationSmoothness));
                        currentPosition = smoothedPosition;
                    }
                    else
                    {
                        currentPosition = jointData.targetPosition;
                    }

                    // Apply the joint transformation based on joint type
                    ApplyJointTransformation(jointTransform, config, currentPosition);
                    jointData.position = currentPosition;
                }
            }
        }
    }

    void ApplyJointTransformation(Transform jointTransform, JointConfig config, float position)
    {
        switch (config.jointType)
        {
            case JointType.Revolute:
            case JointType.Continuous:
                // Apply rotational transformation
                float angle = Mathf.Rad2Deg * position;  // Convert radians to degrees
                // Clamp angle for revolute joints (not for continuous)
                if (config.jointType == JointType.Revolute)
                {
                    angle = Mathf.Clamp(angle, config.minAngle, config.maxAngle);
                }
                jointTransform.localRotation = Quaternion.AngleAxis(angle, config.rotationAxis);
                break;

            case JointType.Prismatic:
                // Apply linear transformation
                float linearPosition = position;
                // Clamp position for prismatic joints
                linearPosition = Mathf.Clamp(linearPosition, config.minPosition, config.maxPosition);
                jointTransform.localPosition = config.positionAxis * linearPosition;
                break;

            case JointType.Fixed:
                // No transformation for fixed joints
                break;
        }
    }

    JointConfig GetJointConfig(string jointName)
    {
        foreach (JointConfig config in jointConfigs)
        {
            if (config.jointName == jointName)
            {
                return config;
            }
        }
        return null;
    }

    // Public methods for external control
    public void SetJointPosition(string jointName, float position)
    {
        if (jointStates.ContainsKey(jointName))
        {
            jointStates[jointName].targetPosition = position;
        }
    }

    public float GetJointPosition(string jointName)
    {
        if (jointStates.ContainsKey(jointName))
        {
            return jointStates[jointName].position;
        }
        return 0f;
    }

    public void SetAnimationSmoothness(float smoothness)
    {
        animationSmoothness = Mathf.Max(0.001f, smoothness); // Prevent division by zero
    }

    public void SetJointInterpolationEnabled(bool enabled)
    {
        enableJointInterpolation = enabled;
    }

    // Method to update joint configuration at runtime
    public void UpdateJointConfig(JointConfig newConfig)
    {
        for (int i = 0; i < jointConfigs.Length; i++)
        {
            if (jointConfigs[i].jointName == newConfig.jointName)
            {
                jointConfigs[i] = newConfig;
                return;
            }
        }

        // If joint config doesn't exist, add it
        JointConfig[] newConfigs = new JointConfig[jointConfigs.Length + 1];
        jointConfigs.CopyTo(newConfigs, 0);
        newConfigs[jointConfigs.Length] = newConfig;
        jointConfigs = newConfigs;
    }

    // Method to get joint information
    public JointStateData GetJointState(string jointName)
    {
        if (jointStates.ContainsKey(jointName))
        {
            return jointStates[jointName];
        }
        return null;
    }

    // Method to get all joint names
    public string[] GetJointNames()
    {
        return jointStates.Keys.ToArray();
    }

    void OnDestroy()
    {
        if (ros != null)
        {
            ros.Dispose();
        }
    }
}