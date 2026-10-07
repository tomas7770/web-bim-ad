from server import *

import time

def initTypes():
    global wood, floorSlabType, extWallType, intWallType

    wood = createMaterial(albedo = [0.463, 0.388, 0.255], name = "Wood")
    floorSlabType = createSlabType(material = wood)
    brick = createMaterial(albedo = [0.667, 0.392, 0.412], name = "Brick")
    extWallType = createWallType(thickness = 0.4, name = "Exterior Wall", material = brick)
    intWallType = createWallType(thickness = 0.12, name = "Interior Wall")

def slab(length, width, level):
    return createSlab({"start": (0, 0), "end": (width, length)}, level, floorSlabType)

def exteriorWalls(length, width, level):
    extWall0 = createWall([(0, 0), (0, length)], level, extWallType)
    extWall1 = createWall([(0, length), (width, length)], level, extWallType)
    extWall2 = createWall([(width, length), (width, 0)], level, extWallType)
    extWall3 = createWall([(width, 0), (0, 0)], level, extWallType)
    return (extWall0, extWall1, extWall2, extWall3)

def interiorWalls(length, width, level, paths):
    intWallsA = []
    intWallsB = []
    for path in paths:
        intWallsA.append(createWall(path, level, intWallType))
        symmetricPath = [(width - path[0][0], length - path[0][1]), (width - path[1][0], length - path[1][1])]
        intWallsB.append(createWall(symmetricPath, level, intWallType))
    return (intWallsA, intWallsB)

def groundFloor(length, width):
    level = 0
    createLevel(level, 0)

    slab(length, width, level)
    extWalls = exteriorWalls(length, width, level)
    intWalls = interiorWalls(length, width, level, [
        [(2, 0), (2, 3.6)],
        [(2, 3.6 + 2.8), (2, 3.6 + 2.8 + 2.9)],
        [(2, 3.6 + 2.8 + 0.6), (2 + 1.45, 3.6 + 2.8 + 0.6)],
        [(2 + 1.45, 3.6 + 2.8 + 0.6), (width, 3.6 + 2.8 + 0.6)],
        [(2 + 1.45, 3.6 + 2.8 + 0.6), (2 + 1.45, 3.6 + 2.8 + 2.9)],
    ])

    # Separators
    middleSeparatorThickness = 2 * (width / 2 - 2 - 1.45)
    separatorThickness = length - 2 * (3.6 + 2.8 + 0.6) - (2.9 - 0.6)
    createWall([(0, 3.6 + 2.8 + 2.9 + separatorThickness / 2),
                (width / 2 + middleSeparatorThickness / 2, 3.6 + 2.8 + 2.9 + separatorThickness / 2)],
                level,
                createWallType(thickness = separatorThickness))
    createWall([(width, length - 3.6 - 2.8 - 2.9 - separatorThickness / 2),
                    (width / 2 - middleSeparatorThickness / 2, length - 3.6 - 2.8 - 2.9 - separatorThickness / 2)],
                    level,
                    createWallType(thickness = separatorThickness))

    # Middle separator
    createWall([(width / 2, 3.6 + 2.8 + 0.6), (width / 2, 3.6 + 2.8 + 2.9)], level,
               createWallType(thickness = middleSeparatorThickness))

    # Windows
    for wall in (extWalls[0], extWalls[2]):
        createWindow(wall, 11.9, 0.1, 0.75, 2.2)
    for wall in (extWalls[1], extWalls[3]):
        createWindow(wall, 0.4, 0.1, 4.8, 2.4)
        createWindow(wall, 5.3, 0, 1, 2.5)

    # Doors
    for wall in (extWalls[0], extWalls[2]):
        createDoor(wall, 0.9, 1.4, 2.1)
    for intWallsL0 in intWalls:
        createDoor(intWallsL0[1], 0.9, 0.9, 2.1)

    # Stairs
    stairType = createStairType(0.91, 0.19, 0.25, wood)
    createStair((0.91, 5.57), (0, 1), level, stairType)
    createStair((width - 0.91, length - 5.57), (0, -1), level, stairType)

def firstFloor(elevation, height, length, width):
    level = 1
    createLevel(level, elevation)

    slabL1 = slab(length, width, level)
    createOpening(slabL1, 0, 5.8, 1, 3.5)
    createOpening(slabL1, width - 1, length - 5.8 - 3.5, 1, 3.5)

    extWalls = exteriorWalls(length, width, level)
    intWalls = interiorWalls(length, width, level, [
        [(0, 5.7), (2, 5.7)],
        [(0, 5.7 + 5.3), (2, 5.7 + 5.3)],
        [(2, 5.7), (2, 5.7 + 5.3)],
        [(2, 5.7 + 0.54), (2 + 1.62, 5.7 + 0.54)],
        [(2, 5.7 + 0.54 + 3.12), (2 + 1.62, 5.7 + 0.54 + 3.12)],
        [(2, 5.7 + 0.54 + 3.12 + 0.92), (2 + 1.62, 5.7 + 0.54 + 3.12 + 0.92)],
    ])

    createWall([(width / 2, 0), (width / 2, length)], level, createWallType(thickness = width - 2 * (2 + 1.62)))

    # Windows
    for wall in (extWalls[0], extWalls[2]):
        createWindow(wall, 5.3, 0.1, 0.75, 2.2)
        createWindow(wall, 13.65, 0.1, 0.8, 0.75)
        createWindow(wall, 13.65, 2 * 0.1 + 0.75, 0.8, 0.75)
        createWindow(wall, 13.65, 3 * 0.1 + 2 * 0.75, 0.8, 0.75)
        createWindow(wall, 14.6, 0.1, 2.8, 2.4)
    for wall in (extWalls[1], extWalls[3]):
        createWindow(wall, 4.7, 0.1, 2.8, 2.4)
        createWindow(wall, 7.6, 0.1, 0.8, 0.75)
        createWindow(wall, 7.6, 2 * 0.1 + 0.75, 0.8, 0.75)
        createWindow(wall, 7.6, 3 * 0.1 + 2 * 0.75, 0.8, 0.75)

    # Doors
    for intWallsL1 in intWalls:
        createDoor(intWallsL1[0], 1, 1, 2.1)
        createDoor(intWallsL1[1], 1, 1, 2.1)
        createDoor(intWallsL1[2], 2.65, 1, 2.1)
        createDoor(intWallsL1[4], 0, 0.85, 2.1)

    # Beams
    createBeam([(0, 0), (width / 2, 0)], level, elevation = height - 0.3)
    createBeam([(width, length), (width / 2, length)], level, elevation = height - 0.3)
    createBeam([(0, length), (0, length - width / 2)], level, elevation = height - 0.3)
    createBeam([(width, 0), (width, width / 2)], level, elevation = height - 0.3)

def roof(elevation, length, width):
    level = 2
    createLevel(level, elevation)
    createRoof([(0, 0), (0, length), (width, length), (width, 0)], level,
               createRoofType(material = createMaterial(albedo = [0, 0.5, 0]))) # [0, 0.616, 0]

def duplex(floor0Height = 3.1, floor1Height = 2.9, length = 17.8, width = 8.8):
    start_time = time.time_ns()

    clear()

    initTypes()
    groundFloor(length, width)
    firstFloor(floor0Height, floor1Height, length, width)
    roof(floor0Height + floor1Height, length, width)

    finish()

    end_time = time.time_ns()
    print(f"Time: {(end_time-start_time)/1e6} ms")
