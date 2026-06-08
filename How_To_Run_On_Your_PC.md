# Running The Project

## Requirements

Make sure the following are installed before you begin:

* Ubuntu 24.04
* ROS 2 Jazzy
* Gazebo Harmonic
* PX4 Autopilot
* QGroundControl
* Micro XRCE Agent
* Python 3.12

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/NoorBalti/UAV-Cyber-Attack.git
cd UAV-Cyber-Attack
```

---

## Step 2: Install Python Packages

```bash
pip install -r src/gps_catcher/gps_catcher/requirements.txt
```

---

## Step 3: Build the ROS Package

```bash
source /opt/ros/jazzy/setup.bash

python3.12 -m colcon build --packages-select gps_catcher

source install/setup.bash
```

---

## Step 4: Disable Direct GPS Connection

Before running the project, disable the direct GPS connection between PX4 and Gazebo.

PX4 should receive GPS data from the ROS nodes instead of directly from Gazebo.

```text
Gazebo GPS
    ↓
listener.py
    ↓
   PX4
```

---

## Step 5: Start PX4

Open a new terminal:

```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```

---

## Step 6: Start Ros2-PX4 Bridge (Bridge-1)

Open another terminal:

```bash
MicroXRCEAgent udp4 -p 8888
```

---

## Step 7: Start Gazebo-Ros2 Bridge (Bridge-2)

Open another terminal:

```bash
source /opt/ros/jazzy/setup.bash

ros2 run ros_gz_bridge parameter_bridge \
/world/default/model/x500_0/link/base_link/sensor/navsat_sensor/navsat@sensor_msgs/msg/NavSatFix[gz.msgs.NavSat
```

---

## Step 8: Start the GPS Listener

Open another terminal inside the project folder:

```bash
source install/setup.bash

ros2 run gps_catcher gps_listener
```

---

## Step 9: Start the GPS Hijacker

Open another terminal inside the project folder:

```bash
source install/setup.bash

ros2 run gps_catcher hijacker
```

---

## Step 10: Open QGroundControl

Open another terminal:

```bash
qgc
```

Wait for the vehicle to connect.

---

# Attack Simulation

Open a new terminal and run the commands below.

## GPS Spoofing

### Set the Fake GPS Location

```bash
ros2 topic pub --once \
/attack_target \
sensor_msgs/msg/NavSatFix \
"{latitude: 47.400, longitude: 8.550, altitude: 20.0}"
```

Replace the coordinates with your desired target location.

### Start the Attack

```bash
ros2 topic pub --once \
/start_attack \
std_msgs/msg/Bool \
"{data: true}"
```

### Stop the Attack

```bash
ros2 topic pub --once \
/start_attack \
std_msgs/msg/Bool \
"{data: false}"
```

---

## Packet Injection Hijacking and Landing

Publish a target landing location:

```bash
ros2 topic pub --once \
/trigger_target_landing \
sensor_msgs/msg/NavSatFix \
"{latitude: 47.397354, longitude: 8.547204, altitude: 0.0}"
```

The UAV will attempt to land at the specified location.
