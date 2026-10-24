-- scenery_scene_script.lua
-- Paste this as a Scene Script in the CoppeliaSim scene.

function createBox(sizeX, sizeY, sizeZ, pos, name)
    local h = sim.createPrimitiveShape(sim.primitiveshape_cuboid, {sizeX, sizeY, sizeZ, 0})
    sim.setObjectName(h, name)
    sim.setObjectPosition(h, -1, pos)
    return h
end

function addPlantDecor()
    -- floor
    local floorHandle = createBox(12, 8, 0.2, {0, 0, -0.1}, "Floor")
    sim.setObjectColor(floorHandle, nil, sim.colorcomponent_ambient_diffuse, {0.18, 0.19, 0.18})

    -- walls
    local wall1 = createBox(12, 0.2, 2.5, {0, -3.8, 1.2}, "WallFront")
    local wall2 = createBox(12, 0.2, 2.5, {0, 3.8, 1.2}, "WallBack")
    local wall3 = createBox(0.2, 8, 2.5, {-5.8, 0, 1.2}, "WallLeft")
    local wall4 = createBox(0.2, 8, 2.5, {5.8, 0, 1.2}, "WallRight")

    sim.setObjectColor(wall1, nil, sim.colorcomponent_ambient_diffuse, {0.42, 0.42, 0.44})
    sim.setObjectColor(wall2, nil, sim.colorcomponent_ambient_diffuse, {0.42, 0.42, 0.44})
    sim.setObjectColor(wall3, nil, sim.colorcomponent_ambient_diffuse, {0.42, 0.42, 0.44})
    sim.setObjectColor(wall4, nil, sim.colorcomponent_ambient_diffuse, {0.42, 0.42, 0.44})

    -- waste bins
    local binPositions = {
        {-3.5, -2.0, 0.35},
        {-2.2, -2.0, 0.35},
        {-0.9, -2.0, 0.35},
        {0.4, -2.0, 0.35},
    }

    for i, pos in ipairs(binPositions) do
        local b = createBox(0.7, 0.7, 0.7, pos, "WasteBin_" .. tostring(i))
        sim.setObjectColor(b, nil, sim.colorcomponent_ambient_diffuse, {0.25, 0.65, 0.25})
    end

    -- conveyor belt and support structure
    local conveyor = createBox(3.5, 0.45, 0.18, {0.5, 0.8, 0.09}, "ConveyorBelt")
    local support1 = createBox(3.5, 0.10, 0.10, {0.5, 0.55, 0.28}, "ConveyorFrame1")
    local support2 = createBox(3.5, 0.10, 0.10, {0.5, 1.05, 0.28}, "ConveyorFrame2")

    sim.setObjectColor(conveyor, nil, sim.colorcomponent_ambient_diffuse, {0.35, 0.35, 0.38})
    sim.setObjectColor(support1, nil, sim.colorcomponent_ambient_diffuse, {0.5, 0.5, 0.52})
    sim.setObjectColor(support2, nil, sim.colorcomponent_ambient_diffuse, {0.5, 0.5, 0.52})

    -- decorative pallets
    local pallet1 = createBox(0.7, 0.7, 0.15, {-3.8, 2.2, 0.07}, "Pallet1")
    local pallet2 = createBox(0.7, 0.7, 0.15, {3.2, 2.2, 0.07}, "Pallet2")
    sim.setObjectColor(pallet1, nil, sim.colorcomponent_ambient_diffuse, {0.45, 0.35, 0.18})
    sim.setObjectColor(pallet2, nil, sim.colorcomponent_ambient_diffuse, {0.45, 0.35, 0.18})
end

function addCameraAndSensor()
    if sim.getObjectHandle("Camera") == -1 then
        local cameraHandle = sim.createCamera(0.1, 100, 60 * math.pi / 180)
        sim.setObjectName(cameraHandle, "Camera")
        sim.setObjectPosition(cameraHandle, -1, {3.8, -1.3, 2.7})
        sim.setObjectOrientation(cameraHandle, -1, {math.rad(45), 0, math.rad(215)})
    end

    if sim.getObjectHandle("ProxSensor") == -1 then
        local proxHandle = sim.createProximitySensor(sim.proximitysensor_pyramid, 0.15, 0.5, 0.0)
        sim.setObjectName(proxHandle, "ProxSensor")
        sim.setObjectPosition(proxHandle, -1, {0.2, 0.0, 0.2})
        sim.setObjectOrientation(proxHandle, -1, {0, 0, math.rad(90)})
    end
end

function sysCall_init()
    addPlantDecor()
    addCameraAndSensor()
    sim.setFloatSignal("belt_speed", 0.05)
end

function sysCall_actuation()
end

function sysCall_cleanup()
end
