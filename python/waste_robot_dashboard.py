import math
import threading
import time
import tkinter as tk
from tkinter import ttk

import numpy as np
from scipy.optimize import minimize

try:
    import sim
except Exception as e:
    print("Could not import sim; make sure the CoppeliaSim remote API is in PYTHONPATH.")
    raise e

# -----------------------------------------------------------
# Robot configuration
# -----------------------------------------------------------
L1 = 0.35
L2 = 0.32
L3 = 0.18
L4 = 0.12

PICKUP_POSE = np.array([0.62, 0.10, 0.22])
DROP_POSE = np.array([0.62, -0.45, 0.22])
HOME_POSE = np.array([0.20, 0.00, 0.40])

JN_LIMS = [
    (-math.pi, math.pi),
    (-2.3, 2.3),
    (-2.6, 2.6),
    (-2.0, 2.0),
]


def clamp(x, lo, hi):
    return max(lo, min(x, hi))


def fk(q):
    q1, q2, q3, q4 = q
    x = (
        L1 * math.cos(q1)
        + L2 * math.cos(q1 + q2)
        + L3 * math.cos(q1 + q2 + q3)
        + L4 * math.cos(q1 + q2 + q3 + q4)
    )
    y = (
        L1 * math.sin(q1)
        + L2 * math.sin(q1 + q2)
        + L3 * math.sin(q1 + q2 + q3)
        + L4 * math.sin(q1 + q2 + q3 + q4)
    )
    z = 0.10
    return np.array([x, y, z])


def objective(q, target_xyz):
    pos = fk(q)
    err = pos - target_xyz
    return float(np.dot(err, err))


def wrap_ik(target_xyz):
    q0 = np.array([0.0, -1.1, 2.0, -0.9], dtype=float)

    def fun(x):
        return objective(x, target_xyz)

    result = minimize(fun, q0, method="L-BFGS-B", bounds=JN_LIMS)
    if result.success:
        return result.x

    best = None
    best_loss = 1e9
    for q1 in np.linspace(-1.6, 1.6, 20):
        for q2 in np.linspace(-1.8, 1.8, 20):
            for q3 in np.linspace(-2.2, 2.2, 20):
                for q4 in np.linspace(-1.5, 1.5, 20):
                    q = np.array([q1, q2, q3, q4], dtype=float)
                    loss = objective(q, target_xyz)
                    if loss < best_loss:
                        best_loss = loss
                        best = q
    if best is not None:
        return best
    raise RuntimeError("IK solver failed")


class CoppeliaRobot:
    def __init__(self):
        self.client_id = -1
        self.joint_handles = {}

    def connect(self, ip="127.0.0.1", port=19997, timeout=5000):
        sim.simxFinish(-1)
        self.client_id = sim.simxStart(ip, port, True, True, timeout, 5)
        if self.client_id == -1:
            raise RuntimeError("Failed to connect to CoppeliaSim Remote API server.")
        self._get_handles()
        print("Connected to CoppeliaSim.")
        return self.client_id

    def _get_handles(self):
        names = ["J1", "J2", "J3", "J4", "GripperLeft", "GripperRight", "ProxSensor"]
        for name in names:
            code, handle = sim.simxGetObjectHandle(self.client_id, name, sim.simx_opmode_blocking)
            if code == sim.simx_return_ok:
                self.joint_handles[name] = handle
                print(f"Handle found: {name} -> {handle}")
            else:
                print(f"Warning: {name} not found, code={code}")

    def set_signal(self, name, value):
        if isinstance(value, float):
            sim.simxSetFloatSignal(self.client_id, name, value, sim.simx_opmode_oneshot)
        elif isinstance(value, int):
            sim.simxSetIntegerSignal(self.client_id, name, value, sim.simx_opmode_oneshot)

    def set_joint_targets(self, q_vals):
        for idx, q in enumerate(q_vals, start=1):
            self.set_signal(f"q{idx}", float(q))

    def set_belt_speed(self, speed):
        self.set_signal("belt_speed", float(speed))

    def start_robot(self):
        self.set_signal("robot_running", 1)

    def stop_robot(self):
        self.set_signal("robot_running", 0)

    def open_gripper(self):
        self.set_signal("gripper_cmd", 0.0)

    def close_gripper(self):
        self.set_signal("gripper_cmd", 1.0)

    def read_proximity(self):
        sensor_handle = self.joint_handles.get("ProxSensor")
        if sensor_handle is None:
            return False
        code, detection_state, _, _, _ = sim.simxReadProximitySensor(
            self.client_id, sensor_handle, sim.simx_opmode_blocking
        )
        return (code == sim.simx_return_ok) and (detection_state > 0)


class RobotController:
    def __init__(self, robot):
        self.robot = robot
        self.running = False
        self.thread = None

    def move_to(self, target_xyz):
        q = wrap_ik(target_xyz)
        print(f"IK solution: {q}")
        self.robot.set_joint_targets(q.tolist())
        time.sleep(0.7)

    def pick_and_place_cycle(self):
        while self.running:
            try:
                self.move_to(HOME_POSE)

                for _ in range(30):
                    if not self.running:
                        return
                    if self.robot.read_proximity():
                        print("Object detected by proximity sensor")
                        break
                    time.sleep(0.1)

                self.move_to(PICKUP_POSE)
                self.robot.close_gripper()
                time.sleep(0.5)

                lifted = PICKUP_POSE.copy()
                lifted[2] = 0.40
                self.move_to(lifted)

                self.move_to(DROP_POSE)
                self.robot.open_gripper()
                time.sleep(0.5)

                self.move_to(HOME_POSE)
                time.sleep(0.5)

            except Exception as exc:
                print(f"Controller error: {exc}")
                self.running = False
                break

    def start(self):
        if self.running:
            return
        self.running = True
        self.robot.start_robot()
        self.robot.set_belt_speed(0.05)
        self.thread = threading.Thread(target=self.pick_and_place_cycle, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        self.robot.stop_robot()
        self.robot.open_gripper()
        self.robot.set_belt_speed(0.0)


class Dashboard:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Waste Collection Robot Dashboard")
        self.root.geometry("540x320")

        self.status_var = tk.StringVar(value="Stopped")
        self.prox_var = tk.StringVar(value="No object")
        self.belt_var = tk.StringVar(value="0.00")
        self.joint_var = tk.StringVar(value="J1: 0.00 | J2: 0.00 | J3: 0.00 | J4: 0.00")

        ttk.Label(root, text="Waste Collection Robot", font=("Arial", 16, "bold")).pack(pady=(10, 4))

        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=8)

        ttk.Button(btn_frame, text="Start", command=self.start_robot).grid(row=0, column=0, padx=6)
        ttk.Button(btn_frame, text="Stop", command=self.stop_robot).grid(row=0, column=1, padx=6)

        ttk.Label(root, text="Status:").pack()
        ttk.Label(root, textvariable=self.status_var, font=("Arial", 12, "bold")).pack()

        ttk.Label(root, text="Proximity:").pack()
        ttk.Label(root, textvariable=self.prox_var, font=("Arial", 11)).pack()

        ttk.Label(root, text="Belt Speed:").pack()
        ttk.Label(root, textvariable=self.belt_var, font=("Arial", 11)).pack()

        ttk.Label(root, text="Joint Angles:").pack()
        ttk.Label(root, textvariable=self.joint_var, font=("Arial", 10)).pack()

        self.update_loop()

    def start_robot(self):
        self.controller.start()
        self.status_var.set("Running")
        self.belt_var.set("0.05")

    def stop_robot(self):
        self.controller.stop()
        self.status_var.set("Stopped")
        self.prox_var.set("No object")
        self.belt_var.set("0.00")

    def update_loop(self):
        try:
            prox = self.controller.robot.read_proximity()
            self.prox_var.set("Object detected" if prox else "No object")
            if self.controller.running:
                self.status_var.set("Running")
            else:
                self.status_var.set("Stopped")
        except Exception:
            pass

        try:
            q1 = sim.simxGetFloatSignal(self.controller.robot.client_id, "q1", sim.simx_opmode_blocking)[1]
            q2 = sim.simxGetFloatSignal(self.controller.robot.client_id, "q2", sim.simx_opmode_blocking)[1]
            q3 = sim.simxGetFloatSignal(self.controller.robot.client_id, "q3", sim.simx_opmode_blocking)[1]
            q4 = sim.simxGetFloatSignal(self.controller.robot.client_id, "q4", sim.simx_opmode_blocking)[1]
            if q1 is not None:
                self.joint_var.set(f"J1: {q1:.2f} | J2: {q2:.2f} | J3: {q3:.2f} | J4: {q4:.2f}")
        except Exception:
            pass

        self.root.after(200, self.update_loop)


if __name__ == "__main__":
    robot = CoppeliaRobot()
    robot.connect()
    robot.open_gripper()
    controller = RobotController(robot)

    root = tk.Tk()
    Dashboard(root, controller)
    root.mainloop()
