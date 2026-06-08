# Running the Project

## Requirements

Make sure the following are already installed:

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

PX4 should receive GPS data from the ROS nodes, not directly from Gazebo.

```text
Gazebo GPS
    ↓
listener.py
    ↓
hijacker.py
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

## Step 6: Start Micro XRCE Agent

Open another terminal:

```bash
MicroXRCEAgent udp4 -p 8888
```

---

## Step 7: Start the GPS Bridge

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

## Step 11: Start the Attack

Open a new terminal and run:

```bash
ros2 topic pub --once /start_attack std_msgs/msg/Bool "{data: true}"
```

---

## Step 12: Set the Fake GPS Location

Example:

```bash
ros2 topic pub --once /attack_target sensor_msgs/msg/NavSatFix "{latitude: 47.400, longitude: 8.550, altitude: 20.0}"
```

Replace the coordinates with your desired location.

---

## Step 13: Stop the Attack

```bash
ros2 topic pub --once /start_attack std_msgs/msg/Bool "{data: false}"
```
