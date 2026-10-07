from server import *

import math
import time

def skyscraper(floorHeight = 4, numberOfFloors = 10, length = 30, width = 20):
    start_time = time.time_ns()

    clear()

    # Constants/parameters
    exteriorColumnWidth = 0.5
    exteriorColumnLength = 0.5
    interiorColumnWidth = 0.25
    interiorColumnLength = 0.25
    interiorColumnThickness = 0.03
    interiorColumnFlangeThickness = 0.02
    columnLengthDistance = 5
    columnWidthDistance = 5
    floorThickness = 0.3
    stairCaseWidth = 3
    stairCaseLength = 5
    windowHeight = 2
    windowWidth = 1
    roofTopThickness = 0.15

    # Levels
    for i in range(numberOfFloors + 1):
        createLevel(i, i * floorHeight)

    # Exterior columns
    exteriorColumnType = createColumnType([
        (0, 0),
        (0, exteriorColumnLength),
        (exteriorColumnWidth, exteriorColumnLength),
        (exteriorColumnWidth, 0)
    ], name = "Exterior Column")

    extColumnX = width - exteriorColumnWidth
    extColumnZ = length - exteriorColumnLength

    exteriorColumnPositions = [
        (0, 0),
        (extColumnX, 0),
        (extColumnX, extColumnZ),
        (0, extColumnZ),
    ]

    for pos in exteriorColumnPositions:
        for i in range(numberOfFloors):
            createColumn(pos, i, exteriorColumnType)

    # Interior columns
    interiorColumnType = createColumnType([
        (interiorColumnWidth / 2, -interiorColumnLength / 2),
        (interiorColumnWidth / 2, -interiorColumnLength / 2 + interiorColumnFlangeThickness),
        (interiorColumnThickness / 2, -interiorColumnLength / 2 + interiorColumnFlangeThickness),
        (interiorColumnThickness / 2, interiorColumnLength / 2 - interiorColumnFlangeThickness),
        (interiorColumnWidth / 2, interiorColumnLength / 2- interiorColumnFlangeThickness),
        (interiorColumnWidth / 2, interiorColumnLength / 2),

        (-interiorColumnWidth / 2, interiorColumnLength / 2),
        (-interiorColumnWidth / 2, interiorColumnLength / 2 - interiorColumnFlangeThickness),
        (-interiorColumnThickness / 2, interiorColumnLength / 2 - interiorColumnFlangeThickness),
        (-interiorColumnThickness / 2, -interiorColumnLength / 2 + interiorColumnFlangeThickness),
        (-interiorColumnWidth / 2, -interiorColumnLength / 2 + interiorColumnFlangeThickness),
        (-interiorColumnWidth / 2, -interiorColumnLength / 2),
    ], name = "Interior Column")

    icLengthCount = math.floor(
        length / columnLengthDistance,
    )
    icWidthCount = math.floor(
        width / columnWidthDistance,
    )

    interiorColumnPositions = []

    for i in range(icLengthCount + 1):
        z = i * columnLengthDistance
        for j in range(icWidthCount + 1):
            isCorner1 = i == 0 and j == 0
            isCorner2 = i == 0 and j == icWidthCount
            isCorner3 = i == icLengthCount and j == 0
            isCorner4 = i == icLengthCount and j == icWidthCount

            if isCorner1 or isCorner2 or isCorner3 or isCorner4:
                continue

            x = j * columnWidthDistance
            interiorColumnPositions.append((x, z))

    columnUuid = None
    for pos in interiorColumnPositions:
        for i in range(numberOfFloors):
            columnUuid = createColumn(pos, i, interiorColumnType, copyUuid = columnUuid)

    # Slabs
    slabType = createSlabType(thickness = floorThickness)
    for i in range(numberOfFloors):
        slab = createSlab({"start": (0, 0), "end": (width, length)}, i, slabType)
        if i > 0:
            createOpening(slab, 0, 0, stairCaseWidth, stairCaseLength)

    # Staircase walls
    for i in range(numberOfFloors):
        createWall([(stairCaseWidth, 0), (stairCaseWidth, stairCaseLength)], i)
        createWall([(0, stairCaseLength), (stairCaseWidth, stairCaseLength)], i)

    # Exterior walls
    exteriorWallType = createWallType(thickness = floorThickness)
    lengthWall = createWall([(0, 0), (0, length)], 0, wallType = exteriorWallType)
    widthWall = createWall([(0, length), (width, length)], 0, wallType = exteriorWallType)
    exteriorWalls = [(lengthWall, length), (widthWall, width)]

    for i in range(numberOfFloors):
        if i > 0:
            exteriorWalls.append((createWall([(0, 0), (0, length)], i, copyUuid = lengthWall, wallType = exteriorWallType), length))
            exteriorWalls.append((createWall([(0, length), (width, length)], i, copyUuid = widthWall, wallType = exteriorWallType), width))
        exteriorWalls.append((createWall([(width, length), (width, 0)], i, copyUuid = lengthWall, wallType = exteriorWallType), length))
        exteriorWalls.append((createWall([(width, 0), (0, 0)], i, copyUuid = widthWall, wallType = exteriorWallType), width))

    # Windows
    for wall in exteriorWalls:
        for i in range(math.floor(wall[1] / windowWidth)):
            createWindow(wall[0], i * windowWidth + 0.1, 0.1, windowWidth - 0.2, windowHeight - 0.2)

    # Roof
    roofType = createRoofType(thickness = floorThickness)
    roof = createRoof([(0, 0), (width, 0), (width, length), (0, length)], numberOfFloors, roofType)
    createOpeningPoly(roof, [(0, 0), (stairCaseWidth, 0), (stairCaseWidth, stairCaseLength), (0, stairCaseLength)])
    roofTopType = createWallType(thickness = roofTopThickness)
    createWall([(0, 0), (0, length)], numberOfFloors, height = windowHeight, wallType = roofTopType)
    createWall([(0, length), (width, length)], numberOfFloors, height = windowHeight, wallType = roofTopType)
    createWall([(width, length), (width, 0)], numberOfFloors, height = windowHeight, wallType = roofTopType)
    createWall([(width, 0), (0, 0)], numberOfFloors, height = windowHeight, wallType = roofTopType)

    finish()

    end_time = time.time_ns()
    print(f"Time: {(end_time-start_time)/1e6} ms")
