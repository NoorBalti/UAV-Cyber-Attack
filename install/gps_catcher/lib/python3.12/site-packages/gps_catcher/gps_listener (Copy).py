import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
from px4_msgs.msg import SensorGps 

class GpsSpoofer(Node):
    def __init__(self):
        super().__init__('gps_spoofer_node')
        self.last_lat = None
        self.last_lon = None
        self.last_alt = None
        self.last_time = None


        # 1. Catch the true GPS from Gazebo
        gz_topic = '/world/default/model/x500_0/link/base_link/sensor/navsat_sensor/navsat'
        self.subscription = self.create_subscription(NavSatFix, gz_topic, self.gps_callback, 10)

        # 2. Feed data into PX4
        self.publisher = self.create_publisher(SensorGps, '/fmu/in/sensor_gps', 10)

    def gps_callback(self, msg):
        # 1. Extract exact Simulation Time from Gazebo's message header!
        # Convert seconds and nanoseconds into absolute microseconds
        timestamp_us = int(msg.header.stamp.sec * 1_000_000 + msg.header.stamp.nanosec / 1000)
        current_time_sec = timestamp_us / 1_000_000.0

        # 2. --- THROTTLE TO 5 Hz (Using Sim Time) ---
        if not hasattr(self, 'last_publish_time'):
            self.last_publish_time = 0.0

        if (current_time_sec - self.last_publish_time) < 0.2:
            return 
            
        self.last_publish_time = current_time_sec
        # --------------------------------------------

        px4_msg = SensorGps()
        
        vel_n = 0.0
        vel_e = 0.0
        vel_d = 0.0

        # Calculate velocity using the accurate simulation time delta
        if hasattr(self, 'last_time') and self.last_time is not None:
            dt = current_time_sec - self.last_time
            if 0.0 < dt < 2.0: 
                d_lat = msg.latitude - getattr(self, 'last_lat', msg.latitude)
                d_lon = msg.longitude - getattr(self, 'last_lon', msg.longitude)
                d_alt = msg.altitude - getattr(self, 'last_alt', msg.altitude)
                
                vel_n = (d_lat * 111320.0) / dt
                vel_e = (d_lon * 111320.0 * math.cos(math.radians(msg.latitude))) / dt
                vel_d = -(d_alt) / dt
        
        self.last_lat = msg.latitude
        self.last_lon = msg.longitude
        self.last_alt = msg.altitude
        self.last_time = current_time_sec

        # --- THE TRANSLATION ---
        # Inject the perfectly synchronized Gazebo time into PX4
        px4_msg.timestamp = timestamp_us
        px4_msg.timestamp_sample = timestamp_us
        px4_msg.time_utc_usec = timestamp_us # Fills the UTC field just in case
        
        px4_msg.latitude_deg = float(msg.latitude) 
        px4_msg.longitude_deg = float(msg.longitude)
        px4_msg.altitude_msl_m = float(msg.altitude)
        px4_msg.altitude_ellipsoid_m = float(msg.altitude)

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
        self.get_logger().info(f'Fed to PX4 at 5Hz -> Sim Time: {current_time_sec:.1f}s | Spd: {px4_msg.vel_m_s:.2f} m/s')

def main(args=None):
    rclpy.init(args=args)
    node = GpsSpoofer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
