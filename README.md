# Offensive Cyber Attack on UAVs In Simulated Enviroment

In this part of our project, I have implemented two things:
  1. Spoofing the drone gps sensor and trying to take it toward a specific location of our own.
  2. Injectiong false packet into c2 links of drone and forcing the drone to move to and land at a location of our own

## Overview

This part of our project provides a ROS 2-based solution for offensive cyber attacks. 
It integrates PX4, MAVLink, and Gazebo simulation to enable testing and development in a simulated enviroment.

### Features

* ROS 2 integration
* PX4 flight controller support
* MAVLink communication
* Gazebo simulation environment
* Real-time telemetry monitoring
* GPS data processing
* Custom ROS 2 nodes and messages

## System Architecture


<img width="889" height="683" alt="image" src="https://github.com/user-attachments/assets/3d577046-7f7a-477e-8cba-c45c19bb0ae1" />



## Project Structure

```text
gps_ws/
├── src/
│   ├── gps_catcher/
│   ├── actuator_msgs/
│   ├── custom_interfaces/
│   └── ...
├── launch/
├── config/
├── scripts/
├── docs/
└── README.md
```

## Requirements

### Software

* Ubuntu 24.04
* ROS 2 Jazzy
* PX4 Autopilot
* Gazebo Harmonic
* Python 3.12

### Python Dependencies

```bash
pip install -r requirements.txt
```

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### Build Workspace

```bash
source /opt/ros/jazzy/setup.bash

cd ~/gps_ws

colcon build

source install/setup.bash
```

## Running the Project

### Launch Simulation

```bash
ros2 launch <package_name> <launch_file>.launch.py
```

### Run Node

```bash
ros2 run <package_name> <node_name>
```

## Example Usage

```bash
ros2 topic echo /gps/fix
```

```bash
ros2 topic list
```

## Configuration

Configuration files are located in:

```text
config/
```

Adjust parameters as needed before launching the system.

## Results

Example outputs:

* GPS coordinates received successfully
* UAV telemetry streamed through ROS 2
* Simulation running in Gazebo

## Future Work

* Sensor fusion integration
* Autonomous navigation
* Mission planning support
* Multi-UAV coordination

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Open a pull request

## License

Specify the project license here.

## Author

Your Name

GitHub: https://github.com/yourusername
