# UAV-Cyber-Attack

> A ROS 2 and PX4-based framework for simulating GPS spoofing attacks against autonomous UAVs in a Software-In-The-Loop (SITL) environment.

![PX4](https://img.shields.io/badge/PX4-Autopilot-blue)
![ROS2](https://img.shields.io/badge/ROS2-Jazzy-success)
![Gazebo](https://img.shields.io/badge/Gazebo-Harmonic-orange)
![Python](https://img.shields.io/badge/Python-3.12-yellow)

---

## Overview

Modern autonomous drones rely heavily on Global Navigation Satellite Systems (GNSS) for localization and navigation. This project investigates the impact of GPS spoofing attacks on UAVs by creating a realistic simulation environment using PX4, Gazebo Harmonic, ROS 2 Jazzy, and QGroundControl.

The framework enables researchers and students to:

* Simulate GPS spoofing attacks
* Analyze UAV behavior under malicious navigation data
* Test attack-detection and mitigation strategies
* Study cyber-physical security threats against autonomous systems

---

## Features

* PX4 Software-In-The-Loop (SITL) simulation
* Gazebo Harmonic integration
* Real-time GPS sensor bridging
* Custom ROS 2 GPS listener node
* Custom GPS hijacker/spoofer node
* Dynamic attack target injection
* Attack activation/deactivation controls
* Automated target landing functionality
* QGroundControl integration
* Modular ROS 2 architecture

---

## System Architecture

```text
                     ┌─────────────────┐
                     │ Gazebo Harmonic │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │ GPS Sensor Data │
                     └────────┬────────┘
                              │
                              ▼
                ┌─────────────────────────┐
                │ ROS-Gazebo Bridge       │
                └──────────┬──────────────┘
                           │
                           ▼
                ┌─────────────────────────┐
                │ GPS Listener Node       │
                └──────────┬──────────────┘
                           │
                           ▼
                ┌─────────────────────────┐
                │ GPS Hijacker Node       │
                └──────────┬──────────────┘
                           │
                           ▼
                ┌─────────────────────────┐
                │ PX4 Autopilot           │
                └──────────┬──────────────┘
                           │
                           ▼
                ┌─────────────────────────┐
                │ QGroundControl          │
                └─────────────────────────┘
```

---

## Technology Stack

| Component      | Version       |
| -------------- | ------------- |
| Ubuntu         | 24.04 LTS     |
| ROS 2          | Jazzy         |
| PX4            | Latest Stable |
| Gazebo         | Harmonic      |
| Python         | 3.12          |
| QGroundControl | Latest        |
| MicroXRCEAgent | Latest        |

---

## Repository Structure

```text
gps_ws/
│
├── src/
│   ├── gps_catcher/
│   │   ├── listener.py
│   │   ├── hijacker.py
│   │   └── ...
│   │
│   └── px4_msgs/
│
├── build/
├── install/
└── log/
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/NoorBalti/UAV-Cyber-Attack.git
cd UAV-Cyber-Attack
```

### Build Workspace

```bash
source /opt/ros/jazzy/setup.bash

cd ~/gps_ws

colcon build --packages-select gps_catcher

source install/setup.bash
```

---

# Running the Simulation

## Terminal 1 — PX4 SITL + Gazebo

```bash
cd ~/PX4-Autopilot

make px4_sitl gz_x500
```

---

## Terminal 2 — Micro XRCE Agent

```bash
MicroXRCEAgent udp4 -p 8888
```

---

## Terminal 3 — ROS-Gazebo Bridge

```bash
source /opt/ros/jazzy/setup.bash

ros2 run ros_gz_bridge parameter_bridge \
/world/default/model/x500_0/link/base_link/sensor/navsat_sensor/navsat@sensor_msgs/msg/NavSatFix[gz.msgs.NavSat
```

---

## Terminal 4 — GPS Listener

```bash
source /opt/ros/jazzy/setup.bash

cd ~/gps_ws

source install/setup.bash

ros2 run gps_catcher gps_listener
```

---

## Terminal 5 — GPS Hijacker

```bash
source /opt/ros/jazzy/setup.bash

cd ~/gps_ws

source install/setup.bash

ros2 run gps_catcher hijacker
```

---

## Terminal 6 — QGroundControl

```bash
qgc
```

---

# Attack Simulation

## Publish Attack Target

```bash
ros2 topic pub --once \
/attack_target \
sensor_msgs/msg/NavSatFix \
"{latitude: 47.400, longitude: 8.550, altitude: 20.0}"
```

## Start Attack

```bash
ros2 topic pub --once \
/start_attack \
std_msgs/msg/Bool \
"{data: true}"
```

## Stop Attack

```bash
ros2 topic pub --once \
/start_attack \
std_msgs/msg/Bool \
"{data: false}"
```

---

# Trigger Autonomous Landing

```bash
ros2 topic pub --once \
/trigger_target_landing \
sensor_msgs/msg/NavSatFix \
"{latitude: 47.397354, longitude: 8.547204, altitude: 0.0}"
```

---

# Research Applications

* UAV Cybersecurity Research
* GNSS Security Testing
* GPS Spoofing Detection
* Autonomous Navigation Security
* Cyber-Physical Systems Security
* Resilient Positioning Systems
* Drone Security Education

---

# Future Work

* Multi-UAV attack scenarios
* GPS spoofing detection algorithms
* Machine-learning-based anomaly detection
* Sensor fusion resilience testing
* Hardware-in-the-Loop (HITL) support
* Real-time attack visualization dashboard

---

# Disclaimer

This project is intended solely for academic, educational, and defensive cybersecurity research purposes within controlled simulation environments.

The authors do not endorse or encourage unauthorized testing on real-world systems, vehicles, networks, or infrastructure.

---

# Author

**Noor Ali**

* GitHub: https://github.com/NoorBalti
* Research Area: UAV Security, Robotics, Reinforcement Learning, Autonomous Systems

---

## Citation

If you use this project in your research, please cite it appropriately.

```bibtex
@software{uav_cyber_attack,
  author = {Noor Ali},
  title = {UAV-Cyber-Attack},
  year = {2026},
  url = {https://github.com/NoorBalti/UAV-Cyber-Attack}
}
```
