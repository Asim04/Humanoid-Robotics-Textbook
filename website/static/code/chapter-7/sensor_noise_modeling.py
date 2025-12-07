#!/usr/bin/env python3
"""
File: sensor_noise_modeling.py
Purpose: Model realistic sensor noise for simulation
Chapter: 7 - Advanced Simulation Techniques
Dependencies: rclpy, sensor_msgs, std_msgs, numpy
Hardware: Simulated sensors in Gazebo
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Imu, NavSatFix, PointCloud2, PointField
from geometry_msgs.msg import Vector3, Quaternion
from std_msgs.msg import Header
import numpy as np
import math
from collections import deque
import sensor_msgs.point_cloud2 as pc2
from std_msgs.msg import Float32


class SensorNoiseModel:
    """Base class for sensor noise modeling."""

    def __init__(self, mean=0.0, std_dev=1.0, bias=0.0, drift_rate=0.0):
        self.mean = mean
        self.std_dev = std_dev
        self.bias = bias
        self.drift_rate = drift_rate  # How fast bias changes over time
        self.current_bias = bias
        self.last_update_time = 0.0

    def add_noise(self, signal, timestamp=None):
        """Add noise to a signal."""
        # Add Gaussian noise
        noise = np.random.normal(self.mean, self.std_dev)

        # Update bias if drift is enabled
        if timestamp and self.drift_rate != 0.0:
            if self.last_update_time == 0.0:
                self.last_update_time = timestamp
            else:
                time_diff = timestamp - self.last_update_time
                self.current_bias += np.random.normal(0, self.drift_rate * time_diff)
                self.last_update_time = timestamp

        return signal + noise + self.current_bias


class LiDARNoiseModel(SensorNoiseModel):
    """Noise model for LiDAR sensors."""

    def __init__(self):
        super().__init__()
        self.range_bias = 0.01  # 1cm bias
        self.range_std_dev = 0.02  # 2cm std dev
        self.intensity_bias = 0.0
        self.intensity_std_dev = 0.1

    def add_noise_to_scan(self, ranges, intensities=None):
        """Add noise to LiDAR scan data."""
        noisy_ranges = []
        noisy_intensities = []

        for i, range_val in enumerate(ranges):
            if not (math.isnan(range_val) or math.isinf(range_val)):
                # Add distance-dependent noise (further distances have more noise)
                distance_factor = min(range_val / 10.0, 1.0)  # Normalize by max range
                range_noise_std = self.range_std_dev * (1.0 + distance_factor)

                noisy_range = range_val + np.random.normal(0, range_noise_std)
                # Ensure positive range values
                noisy_ranges.append(max(0.01, noisy_range))  # Minimum 1cm
            else:
                noisy_ranges.append(range_val)

        if intensities is not None:
            for intensity in intensities:
                noisy_intensity = intensity + np.random.normal(
                    self.intensity_bias,
                    self.intensity_std_dev
                )
                noisy_intensities.append(max(0, noisy_intensity))

        return noisy_ranges, (noisy_intensities if intensities is not None else None)


class IMUNoiseModel:
    """Noise model for IMU sensors."""

    def __init__(self):
        # Gyroscope noise parameters
        self.gyro_noise_density = 1.6e-4  # rad/s/sqrt(Hz)
        self.gyro_random_walk = 1.6e-5  # rad/s^2/sqrt(Hz)
        self.gyro_bias_instability = 3.5e-5  # rad/s
        self.gyro_bias_correlation_time = 1.0e4  # s

        # Accelerometer noise parameters
        self.accel_noise_density = 1.6e-3  # m/s^2/sqrt(Hz)
        self.accel_random_walk = 1.6e-4  # m/s^3/sqrt(Hz)
        self.accel_bias_instability = 3.5e-4  # m/s^2
        self.accel_bias_correlation_time = 1.0e4  # s

        # Bias random walk integrators
        self.gyro_bias_rw = np.array([0.0, 0.0, 0.0])
        self.accel_bias_rw = np.array([0.0, 0.0, 0.0])

        # Correlated bias (first-order Gauss-Markov process)
        self.gyro_bias_corr = np.array([0.0, 0.0, 0.0])
        self.accel_bias_corr = np.array([0.0, 0.0, 0.0])

    def add_noise_to_imu(self, angular_velocity, linear_acceleration, dt):
        """Add realistic noise to IMU measurements."""
        # Update bias random walk
        self.gyro_bias_rw += np.random.normal(0, self.gyro_random_walk * math.sqrt(dt), 3)
        self.accel_bias_rw += np.random.normal(0, self.accel_random_walk * math.sqrt(dt), 3)

        # Update correlated bias (Gauss-Markov process)
        gyro_corr_decay = math.exp(-dt / self.gyro_bias_correlation_time)
        accel_corr_decay = math.exp(-dt / self.accel_bias_correlation_time)

        self.gyro_bias_corr = (gyro_corr_decay * self.gyro_bias_corr +
                              np.random.normal(0, self.gyro_bias_instability * math.sqrt(dt), 3))
        self.accel_bias_corr = (accel_corr_decay * self.accel_bias_corr +
                               np.random.normal(0, self.accel_bias_instability * math.sqrt(dt), 3))

        # Add noise to measurements
        gyro_noise = np.random.normal(0, self.gyro_noise_density / math.sqrt(dt), 3)
        accel_noise = np.random.normal(0, self.accel_noise_density / math.sqrt(dt), 3)

        noisy_angular_velocity = (np.array(angular_velocity) +
                                 gyro_noise +
                                 self.gyro_bias_rw +
                                 self.gyro_bias_corr)

        noisy_linear_acceleration = (np.array(linear_acceleration) +
                                    accel_noise +
                                    self.accel_bias_rw +
                                    self.accel_bias_corr)

        return noisy_angular_velocity.tolist(), noisy_linear_acceleration.tolist()


class GNSsNoiseModel(SensorNoiseModel):
    """Noise model for GPS sensors."""

    def __init__(self):
        super().__init__()
        self.horizontal_accuracy = 1.0  # meters
        self.vertical_accuracy = 2.0    # meters
        self.velocity_accuracy = 0.1    # m/s

    def add_noise_to_gps(self, latitude, longitude, altitude, velocity):
        """Add noise to GPS measurements."""
        # Convert position errors to latitude/longitude changes
        # Approximate: 1 degree latitude ~ 111320 meters
        lat_noise = np.random.normal(0, self.horizontal_accuracy / 111320.0)
        lon_noise = np.random.normal(0, self.horizontal_accuracy / (111320.0 * math.cos(math.radians(latitude))))
        alt_noise = np.random.normal(0, self.vertical_accuracy)

        noisy_lat = latitude + lat_noise
        noisy_lon = longitude + lon_noise
        noisy_alt = altitude + alt_noise

        # Add noise to velocity
        noisy_velocity = [
            velocity[0] + np.random.normal(0, self.velocity_accuracy),
            velocity[1] + np.random.normal(0, self.velocity_accuracy),
            velocity[2] + np.random.normal(0, self.velocity_accuracy)
        ]

        return noisy_lat, noisy_lon, noisy_alt, noisy_velocity


class SensorNoiseSimulator(Node):
    """
    Node that simulates realistic sensor noise and publishes noisy sensor data.
    """

    def __init__(self):
        super().__init__('sensor_noise_simulator')

        # Initialize noise models
        self.lidar_noise_model = LiDARNoiseModel()
        self.imu_noise_model = IMUNoiseModel()
        self.gps_noise_model = GNSsNoiseModel()

        # Previous timestamp for IMU noise modeling
        self.prev_time = self.get_clock().now()

        # Publishers
        self.noisy_scan_pub = self.create_publisher(LaserScan, '/noisy_scan', 10)
        self.noisy_imu_pub = self.create_publisher(Imu, '/noisy_imu', 10)
        self.noisy_gps_pub = self.create_publisher(NavSatFix, '/noisy_gps', 10)
        self.noisy_pointcloud_pub = self.create_publisher(PointCloud2, '/noisy_pointcloud', 10)

        # Subscribers (to get clean sensor data)
        self.clean_scan_sub = self.create_subscription(
            LaserScan, '/clean_scan', self.scan_callback, 10
        )
        self.clean_imu_sub = self.create_subscription(
            Imu, '/clean_imu', self.imu_callback, 10
        )
        self.clean_gps_sub = self.create_subscription(
            NavSatFix, '/clean_gps', self.gps_callback, 10
        )

        # Timer for continuous noise generation
        self.noise_timer = self.create_timer(0.1, self.generate_continuous_noise)

        # Noise level publisher for monitoring
        self.noise_level_pub = self.create_publisher(Float32, '/sensor_noise/level', 10)

        self.get_logger().info('Sensor noise simulator initialized')

    def scan_callback(self, msg):
        """Process clean LiDAR scan and add noise."""
        # Add noise to ranges
        noisy_ranges, _ = self.lidar_noise_model.add_noise_to_scan(msg.ranges)

        # Create noisy message
        noisy_msg = LaserScan()
        noisy_msg.header = Header()
        noisy_msg.header.stamp = self.get_clock().now().to_msg()
        noisy_msg.header.frame_id = msg.header.frame_id
        noisy_msg.angle_min = msg.angle_min
        noisy_msg.angle_max = msg.angle_max
        noisy_msg.angle_increment = msg.angle_increment
        noisy_msg.time_increment = msg.time_increment
        noisy_msg.scan_time = msg.scan_time
        noisy_msg.range_min = msg.range_min
        noisy_msg.range_max = msg.range_max
        noisy_msg.ranges = noisy_ranges
        noisy_msg.intensities = msg.intensities  # We'll add intensity noise separately if needed

        self.noisy_scan_pub.publish(noisy_msg)

    def imu_callback(self, msg):
        """Process clean IMU data and add noise."""
        # Calculate time difference for noise modeling
        current_time = rclpy.time.Time.from_msg(msg.header.stamp)
        dt = (current_time.nanoseconds - self.prev_time.nanoseconds) / 1e9
        if dt <= 0:
            dt = 0.01  # Default to 10ms if time is not progressing

        # Add noise to measurements
        noisy_angular_velocity, noisy_linear_acceleration = self.imu_noise_model.add_noise_to_imu(
            [msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z],
            [msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z],
            dt
        )

        # Create noisy IMU message
        noisy_msg = Imu()
        noisy_msg.header = Header()
        noisy_msg.header.stamp = self.get_clock().now().to_msg()
        noisy_msg.header.frame_id = msg.header.frame_id

        # Copy orientation (assuming it's already processed)
        noisy_msg.orientation = msg.orientation

        # Add noise to angular velocity
        noisy_msg.angular_velocity.x = noisy_angular_velocity[0]
        noisy_msg.angular_velocity.y = noisy_angular_velocity[1]
        noisy_msg.angular_velocity.z = noisy_angular_velocity[2]

        # Add noise to linear acceleration
        noisy_msg.linear_acceleration.x = noisy_linear_acceleration[0]
        noisy_msg.linear_acceleration.y = noisy_linear_acceleration[1]
        noisy_msg.linear_acceleration.z = noisy_linear_acceleration[2]

        # Add covariance matrices (these represent the noise characteristics)
        # Angular velocity covariance
        noisy_msg.angular_velocity_covariance = [
            self.imu_noise_model.gyro_noise_density**2,
            0.0, 0.0,
            0.0, self.imu_noise_model.gyro_noise_density**2, 0.0,
            0.0, 0.0, self.imu_noise_model.gyro_noise_density**2
        ]

        # Linear acceleration covariance
        noisy_msg.linear_acceleration_covariance = [
            self.imu_noise_model.accel_noise_density**2,
            0.0, 0.0,
            0.0, self.imu_noise_model.accel_noise_density**2, 0.0,
            0.0, 0.0, self.imu_noise_model.accel_noise_density**2
        ]

        self.noisy_imu_pub.publish(noisy_msg)
        self.prev_time = current_time

    def gps_callback(self, msg):
        """Process clean GPS data and add noise."""
        # Add noise to GPS measurements
        noisy_lat, noisy_lon, noisy_alt, noisy_velocity = self.gps_noise_model.add_noise_to_gps(
            msg.latitude, msg.longitude, msg.altitude,
            [0.0, 0.0, 0.0]  # Placeholder for velocity if not available
        )

        # Create noisy GPS message
        noisy_msg = NavSatFix()
        noisy_msg.header = Header()
        noisy_msg.header.stamp = self.get_clock().now().to_msg()
        noisy_msg.header.frame_id = msg.header.frame_id
        noisy_msg.status = msg.status
        noisy_msg.latitude = noisy_lat
        noisy_msg.longitude = noisy_lon
        noisy_msg.altitude = noisy_alt

        # Add position covariance (represents uncertainty)
        horizontal_variance = self.gps_noise_model.horizontal_accuracy**2
        vertical_variance = self.gps_noise_model.vertical_accuracy**2

        noisy_msg.position_covariance = [
            horizontal_variance, 0.0, 0.0,
            0.0, horizontal_variance, 0.0,
            0.0, 0.0, vertical_variance
        ]
        noisy_msg.position_covariance_type = NavSatFix.COVARIANCE_TYPE_APPROXIMATED

        self.noisy_gps_pub.publish(noisy_msg)

    def generate_continuous_noise(self):
        """Generate continuous noise data for sensors that don't have clean counterparts."""
        # Publish noise level for monitoring
        noise_level_msg = Float32()
        noise_level_msg.data = 0.5  # Placeholder - could be calculated based on current noise
        self.noise_level_pub.publish(noise_level_msg)

    def create_noisy_pointcloud(self, clean_points):
        """Create a noisy point cloud from clean points."""
        noisy_points = []
        for point in clean_points:
            # Add noise to each coordinate
            noisy_x = point[0] + np.random.normal(0, 0.01)  # 1cm std dev
            noisy_y = point[1] + np.random.normal(0, 0.01)
            noisy_z = point[2] + np.random.normal(0, 0.02)  # Slightly more noise in Z
            noisy_points.append([noisy_x, noisy_y, noisy_z])

        # Create PointCloud2 message
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = 'sensor_frame'

        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1)
        ]

        # Pack points into binary data
        data = []
        for point in noisy_points:
            data.append(struct.pack('fff', point[0], point[1], point[2]))

        pointcloud_msg = PointCloud2()
        pointcloud_msg.header = header
        pointcloud_msg.height = 1
        pointcloud_msg.width = len(noisy_points)
        pointcloud_msg.fields = fields
        pointcloud_msg.is_bigendian = False
        pointcloud_msg.point_step = 12  # 3 floats * 4 bytes each
        pointcloud_msg.row_step = pointcloud_msg.point_step * pointcloud_msg.width
        pointcloud_msg.is_dense = True
        pointcloud_msg.data = b''.join(data)

        return pointcloud_msg


def main(args=None):
    rclpy.init(args=args)

    sensor_noise_simulator = SensorNoiseSimulator()

    try:
        rclpy.spin(sensor_noise_simulator)
    except KeyboardInterrupt:
        pass
    finally:
        sensor_noise_simulator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()