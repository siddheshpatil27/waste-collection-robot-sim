-- robot_child_script.lua
-- Paste this as a Child Script on the robot model in CoppeliaSim.
-- The robot model must have joints named exactly:
-- "J1", "J2", "J3", "J4", "GripperLeft", "GripperRight"
-- and a proximity sensor named "ProxSensor"

local jointHandles = {}
local gripperLeft
local gripperRight
local proxSensor

function clamp(v, lo, hi)
    if v < lo then return lo end
    if v > hi then return hi end
    return v
end

function sysCall_init()
    jointHandles[1] = sim.getObjectHandle("J1")
    jointHandles[2] = sim.getObjectHandle("J2")
    jointHandles[3] = sim.getObjectHandle("J3")
    jointHandles[4] = sim.getObjectHandle("J4")

    gripperLeft = sim.getObjectHandle("GripperLeft")
    gripperRight = sim.getObjectHandle("GripperRight")
    proxSensor = sim.getObjectHandle("ProxSensor")

    for i = 1, #jointHandles do
        sim.setJointMode(jointHandles[i], sim.jointmode_force)
        sim.setJointTargetPosition(jointHandles[i], 0)
    end

    sim.setJointTargetPosition(gripperLeft, 0.0)
    sim.setJointTargetPosition(gripperRight, 0.0)

    sim.setIntegerSignal("robot_running", 1)
    sim.setFloatSignal("belt_speed", 0.05)
end

function sysCall_actuation()
    local running = sim.getIntegerSignal("robot_running") or 0

    local q1 = sim.getFloatSignal("q1") or 0
    local q2 = sim.getFloatSignal("q2") or 0
    local q3 = sim.getFloatSignal("q3") or 0
    local q4 = sim.getFloatSignal("q4") or 0

    if running == 1 then
        sim.setJointTargetPosition(jointHandles[1], q1)
        sim.setJointTargetPosition(jointHandles[2], q2)
        sim.setJointTargetPosition(jointHandles[3], q3)
        sim.setJointTargetPosition(jointHandles[4], q4)
    else
        for i = 1, #jointHandles do
            sim.setJointTargetPosition(jointHandles[i], sim.getJointPosition(jointHandles[i]))
        end
    end

    local gripperCmd = sim.getFloatSignal("gripper_cmd") or 0
    local target = clamp(gripperCmd, 0, 1)

    if target < 0.5 then
        sim.setJointTargetPosition(gripperLeft, 0.0)
        sim.setJointTargetPosition(gripperRight, 0.0)
    else
        sim.setJointTargetPosition(gripperLeft, 0.03)
        sim.setJointTargetPosition(gripperRight, -0.03)
    end

    local detection = sim.readProximitySensor(proxSensor)
    if detection then
        sim.setIntegerSignal("prox_detected", 1)
    else
        sim.setIntegerSignal("prox_detected", 0)
    end
end

function sysCall_cleanup()
end
