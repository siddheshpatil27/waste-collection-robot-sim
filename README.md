# Waste Collection Pick-and-Place Robot in CoppeliaSim

This project contains a complete starter setup for a waste collection pick-and-place robot simulation in CoppeliaSim 4.1.0.

It includes:
- A robot arm model control script (Lua child script)
- A plant/environment scenery script (Lua scene script)
- A Python controller with inverse kinematics and dashboard
- Detailed setup and usage instructions

## Project structure

```text
waste-collection-robot-sim/
├── README.md
├── requirements.txt
├── coppeliasim/
│   ├── robot_child_script.lua
│   └── scenery_scene_script.lua
├── python/
│   └── waste_robot_dashboard.py
└── .gitignore
```

## Features

- 4-DOF robotic arm
- Target position control using signals and a Lua child script
- Proximity sensor detection
- Conveyor area and waste collection environment
- Camera setup for monitoring
- Waste bin collection area
- Python control dashboard with Start / Stop / Monitor functions
- Inverse kinematics approximation using SciPy optimization

## Requirements

### CoppeliaSim
- CoppeliaSim 4.1.0
- The scene should expose these objects:
  - J1, J2, J3, J4
  - GripperLeft, GripperRight
  - ProxSensor
  - Camera
  - ConveyorBelt (recommended)

### Python
- Python 3.9+
- SciPy
- Tkinter (usually bundled with Python)

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Setup in CoppeliaSim

### 1. Create the robot model
Create a robot with 4 revolute joints and a simple gripper.
Use the following names for the objects:

- `J1`
- `J2`
- `J3`
- `J4`
- `GripperLeft`
- `GripperRight`

The `robot_child_script.lua` file expects these names exactly.

### 2. Add the proximity sensor
Add a proximity sensor and name it:

- `ProxSensor`

This is used to detect when a waste item arrives near the pickup area.

### 3. Add a camera
Add a camera and name it:

- `Camera`

This camera is intended for visual monitoring of the station.

### 4. Add the scenery
Use the scene script in `coppeliasim/scenery_scene_script.lua` to build:
- floor
- walls
- bins
- conveyor body
- camera and plant decor

### 5. Attach the robot child script
In CoppeliaSim:
- Select the robot model
- Add a Child Script
- Paste the contents of `coppeliasim/robot_child_script.lua`

### 6. Attach the scene script
In CoppeliaSim:
- Select the scene root or a scene-level object
- Add a Script
- Paste the contents of `coppeliasim/scenery_scene_script.lua`

## Running the Python controller

### 1. Start CoppeliaSim
Launch CoppeliaSim 4.1.0 and open the scene.

### 2. Start the simulation
Run the scene in the simulator.

### 3. Run the Python script
From the project root:

```bash
python python/waste_robot_dashboard.py
```

This script will:
- connect to the CoppeliaSim remote API
- send joint goals using `q1`, `q2`, `q3`, `q4`
- compute inverse kinematics
- read proximity sensor state
- show a simple dashboard with Start/Stop actions

## Dashboard behavior

The Python dashboard includes:
- Start button
- Stop button
- Robot status
- Proximity sensor state
- Belt speed
- Joint angle display

## IK and control logic

The Python script uses a simplified 4-joint arm and a nonlinear optimization approach with SciPy.

The main idea is:
- define target 3D positions for pickup and drop zones
- compute inverse kinematics numerically
- convert the result to joint target values
- send them to the robot via CoppeliaSim signals

The file `python/waste_robot_dashboard.py` contains the main configuration with:
- `HOME_POSE`
- `PICKUP_POSE`
- `DROP_POSE`

These values can be tuned to your exact robot geometry and scene.

## Tips for tuning

### Robot geometry tuning
Update these constants in `python/waste_robot_dashboard.py`:

```python
L1 = 0.35
L2 = 0.32
L3 = 0.18
L4 = 0.12
```

These represent link lengths. Adjust them to match your robot model.

### Target pose tuning
Adjust these values if the tool is not reaching the waste area correctly:

```python
PICKUP_POSE = np.array([0.62, 0.10, 0.22])
DROP_POSE   = np.array([0.62, -0.45, 0.22])
HOME_POSE   = np.array([0.20, 0.00, 0.40])
```

### Gripper logic
The child script accepts a float signal named:

- `gripper_cmd`

Values:
- `0.0` = open
- `1.0` = closed

## Common problems and fixes

### 1. Connection failed
If the Python script cannot connect:
- Ensure CoppeliaSim is running
- Ensure the Remote API is enabled
- Confirm the port is correct (`19997` by default)

### 2. Robot does not move
Check:
- object names exactly match (`J1`, `J2`, ...)
- child script is attached to the correct robot model
- the simulation is running
- the `robot_running` signal is set to `1`

### 3. Proximity sensor never triggers
- Confirm sensor name is exactly `ProxSensor`
- Ensure the sensor faces the object path correctly
- Check that the object is entering the sensor detection zone

### 4. IK solution is invalid
- Tune the link lengths
- Tune the target positions
- Increase the search range if needed

## Important notes

This project is intended as a starter simulation framework, not a turnkey industrial-control system.

It is designed to be:
- easy to understand
- easy to modify
- suitable for demonstrations and classroom projects
- expandable for real conveyor tracking and sorting logic

## Future extensions

You can extend this project to include:
- multiple waste categories
- color-based sorting
- object recognition from camera
- conveyor motion based on object detection
- PLC-like state machine for full automation
- MQTT or ROS communication

## License

This project is provided for educational and prototyping use.

---

## Quick start summary

```bash
pip install -r requirements.txt
python python/waste_robot_dashboard.py
```

Then start the CoppeliaSim scene and run the simulation.
