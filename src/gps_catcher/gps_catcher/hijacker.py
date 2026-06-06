import math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data  # <-- Added QoS import
from px4_msgs.msg import VehicleCommand, VehicleGlobalPosition
from sensor_msgs.msg import NavSatFix

class AuthorizedTargetLander(Node):
    def __init__(self):
        super().__init__('authorized_target_lander')
        
        # --- STATE TRACKING ---
        self.state = 'IDLE'
        self.target_lat = None
        self.target_lon = None
        
        self.current_lat = None
        self.current_lon = None
        self.current_alt = None
        
        self.arrival_radius = 2.0  
        self.log_throttle = 0

        # --- PUBLISHERS ---
        self.cmd_pub = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', 10)
        
        # --- SUBSCRIBERS ---
        self.trigger_sub = self.create_subscription(
            NavSatFix, '/trigger_target_landing', self.trigger_callback, 10
        )
        
        # Apply qos_profile_sensor_data to match PX4's Best Effort policy!
        self.pos_sub = self.create_subscription(
            VehicleGlobalPosition, 
            '/fmu/out/vehicle_global_position', 
            self.global_pos_callback, 
            qos_profile_sensor_data  # <-- Fix applied here
        )
        
        self.get_logger().info('✅ Two-Step Target Lander Active. Waiting for target...')

    def global_pos_callback(self, msg):
        self.current_lat = msg.lat
        self.current_lon = msg.lon
        self.current_alt = msg.alt  

        if self.state == 'TRANSIT':
            dn = (self.target_lat - self.current_lat) * 111320.0
            de = (self.target_lon - self.current_lon) * 111320.0 * math.cos(math.radians(self.current_lat))
            dist = math.sqrt(dn**2 + de**2)

            self.log_throttle += 1
            if self.log_throttle % 10 == 0:
                self.get_logger().info(f'✈️ Flying to target... Distance remaining: {dist:.1f}m')

            if dist <= self.arrival_radius:
                self.get_logger().warn('🎯 Arrived at target coordinates! Initiating vertical landing...')
                self.send_command(21) 
                self.state = 'LANDING'

    def trigger_callback(self, msg):
        if self.current_alt is None:
            self.get_logger().error("No telemetry received from PX4 yet. Wait a moment and try again.")
            return

        self.target_lat = msg.latitude
        self.target_lon = msg.longitude
        
        self.get_logger().warn(f'🚀 TARGET RECEIVED: Lat {self.target_lat}, Lon {self.target_lon}')
        self.get_logger().warn(f'Maintaining current altitude of {self.current_alt:.1f}m for transit.')

        self.send_command(
            192, 
            param5=self.target_lat, 
            param6=self.target_lon, 
            param7=self.current_alt 
        )
        
        self.state = 'TRANSIT'
        self.log_throttle = 0

    def send_command(self, command_id, param5=float('nan'), param6=float('nan'), param7=float('nan')):
        command = VehicleCommand()
        command.command = command_id
        
        command.param1 = float('nan')
        command.param2 = float('nan')
        command.param3 = float('nan')
        command.param4 = float('nan')
        
        command.param5 = float(param5)
        command.param6 = float(param6)
        command.param7 = float(param7)
        
        command.target_system = 1
        command.target_component = 1
        command.source_system = 255 
        command.source_component = 0
        command.from_external = True
        
        command.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        
        self.cmd_pub.publish(command)

def main(args=None):
    rclpy.init(args=args)
    node = AuthorizedTargetLander()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()