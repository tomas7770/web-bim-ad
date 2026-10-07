from server import *
from demo import circle

import math
import time

# Vector functions

def scale(u, a):
    return (u[0] * a, u[1] * a)

def rotate(point, deg):
    a = deg * math.pi / 180
    return (point[0] * math.cos(a) - point[1] * math.sin(a), point[0] * math.sin(a) + point[1] * math.cos(a))

def geometricCenter(points):
    meanX = 0
    meanZ = 0
    for p in points:
        meanX += p[0]
        meanZ += p[1]
    meanX /= len(points)
    meanZ /= len(points)
    return (meanX, meanZ)

def dist(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def lerp(u, v, alpha):
    return (u[0] * (1 - alpha) + v[0] * alpha, u[1] * (1 - alpha) + v[1] * alpha)

def lerpDist(u, v, d):
    return lerp(u, v, d / dist(u, v))

def diff(u, v):
    return (u[0] - v[0], u[1] - v[1])

def perpDir(u, sym = False):
    if sym:
        return (-u[1], u[0])
    else:
        return (u[1], -u[0])

def angleFromVec(u):
    return 180 * math.atan2(u[1], u[0]) / math.pi

# Tower

def getLevelPoints(level, planPoints, degreesPerFloor):
    return list(map(lambda p: rotate(p, degreesPerFloor * level), planPoints))

def centralCore(level, slab, coreRadius):
    if level > 0:
        createOpeningPoly(slab, circle(coreRadius, 10))
    createWall(circle(coreRadius, 10, True), level)

def perimeterColumns(level, levelPoints, numColumnsZ, numColumnsHalfX,
                     firstColumnSpacingZ, firstColumnSpacingX,
                     planAngle, degreesPerFloor, perimeterColumnType):

    def columnSpacingZ(i0, i1):
        zLength = dist(levelPoints[i0], levelPoints[i1])
        return (zLength - firstColumnSpacingZ * 2) / (numColumnsZ - 1)

    def columnSpacingX(i0, i1):
        halfXLength = dist(levelPoints[i1], levelPoints[i0])
        return (halfXLength - firstColumnSpacingX) / numColumnsHalfX

    for j in range(numColumnsZ):
        createColumn(lerpDist(levelPoints[3], levelPoints[4], firstColumnSpacingZ + columnSpacingZ(3, 4) * j), level,
                        angle = -angleFromVec(diff(levelPoints[4], levelPoints[3])),
                        columnType = perimeterColumnType)
        createColumn(lerpDist(levelPoints[0], levelPoints[1], firstColumnSpacingZ + columnSpacingZ(0, 1) * j), level,
                        angle = -angleFromVec(diff(levelPoints[1], levelPoints[0])),
                        columnType = perimeterColumnType)
    createColumn(levelPoints[2], level, angle = -planAngle - degreesPerFloor * level, columnType = perimeterColumnType)
    createColumn(levelPoints[5], level, angle = -planAngle - degreesPerFloor * level - 180, columnType = perimeterColumnType)
    for j in range(numColumnsHalfX):
        # Bottom of plan
        createColumn(lerpDist(levelPoints[3], levelPoints[2], firstColumnSpacingX + columnSpacingX(3, 2) * j), level,
                        angle = -angleFromVec(diff(levelPoints[3], levelPoints[2])),
                        columnType = perimeterColumnType)
        createColumn(lerpDist(levelPoints[1], levelPoints[2], firstColumnSpacingX + columnSpacingX(1, 2) * j), level,
                        angle = -angleFromVec(diff(levelPoints[2], levelPoints[1])),
                        columnType = perimeterColumnType)

        # Top of plan
        createColumn(lerpDist(levelPoints[4], levelPoints[5], firstColumnSpacingX + columnSpacingX(4, 5) * j), level,
                        angle = -angleFromVec(diff(levelPoints[5], levelPoints[4])),
                        columnType = perimeterColumnType)
        createColumn(lerpDist(levelPoints[0], levelPoints[5], firstColumnSpacingX + columnSpacingX(0, 5) * j), level,
                        angle = -angleFromVec(diff(levelPoints[0], levelPoints[5])),
                        columnType = perimeterColumnType)

def cornerColumns(level, levelPoints, levelPointsNext, planAngle, degreesPerFloor, cornerColumnType, cornerColumnMirroredType):
    createColumn(levelPoints[0], level, topPosition = levelPointsNext[0], angle = -planAngle - degreesPerFloor * level, columnType = cornerColumnMirroredType)
    createColumn(levelPoints[1], level, topPosition = levelPointsNext[1], angle = -planAngle - degreesPerFloor * level + 180, columnType = cornerColumnType)
    createColumn(levelPoints[3], level, topPosition = levelPointsNext[3], angle = -planAngle - degreesPerFloor * level + 180, columnType = cornerColumnMirroredType)
    createColumn(levelPoints[4], level, topPosition = levelPointsNext[4], angle = -planAngle - degreesPerFloor * level, columnType = cornerColumnType)

def innerCol(level, point, planAngle, degreesPerFloor, innerColumnType):
    createColumn(rotate(point, degreesPerFloor * level), level,
                topPosition = rotate(point, degreesPerFloor * (level + 1)),
                angle = -planAngle - degreesPerFloor * level,
                columnType = innerColumnType)

def innerColumns(level, innerColumnPoints, planAngle, degreesPerFloor, innerColumnType):
    for point in innerColumnPoints:
        innerCol(level, point, planAngle, degreesPerFloor, innerColumnType)

def curtainWall(level, levelPoints, wallType):
    # Modeled as a normal wall
    createWall(levelPoints + [levelPoints[0]], level, wallType = wallType)

def tower():
    start_time = time.time_ns()

    clear()

    planScale = 14
    planAngle = 8.8

    numberOfFloors = 73
    degreesPerFloor = 90 / numberOfFloors
    floorHeight = 306 / numberOfFloors

    planPoints = [
        (-1.862, 1.146),
        (-1.44, -1.414),
        (0.247, -1.392),
        (1.849, -0.854),
        (1.425, 1.705),
        (-0.195, 1.263),
    ]

    numColumnsHalfX = 5
    numColumnsZ = 8
    firstColumnSpacingX = dist((1.425, 1.705), (1.029, 1.591)) * planScale
    firstColumnSpacingZ = dist((1.425, 1.705), (1.492, 1.305)) * planScale

    coreRadius = 0.575 * planScale

    planPoints = list(map(lambda p: scale(p, planScale), planPoints))
    center = geometricCenter(planPoints)
    planPoints = list(map(lambda p: diff(p, center), planPoints))

    innerColumnPoints = [
        (0.925, 0.672),
        (1.01, 0.166),
        (1.095, -0.332),
        (-1.053, 0.338),
        (-0.968, -0.16),
        (-0.886, -0.658),
    ]
    innerColumnPoints = list(map(lambda p: scale(p, planScale), innerColumnPoints))
    innerColumnPoints = list(map(lambda p: diff(p, center), innerColumnPoints))

    reinforcedConcrete = createMaterial(
        albedo = (0.5, 0.5, 0.5),
        texturePath = "./ignore/concrete-2500-mm-architextures.jpg",
        name = "Reinforced Concrete"
    )

    pcLength = planScale * dist((-0.058, 0.278), (-0.087, 0.156))
    pcHalfWidth = planScale * dist((-0.058, 0.278), (0.016, 0.256)) / 2
    perimeterColumnType = createColumnType(profile = [
        (pcHalfWidth, 0),
        (pcHalfWidth, pcLength),
        (-pcHalfWidth, pcLength),
        (-pcHalfWidth, 0),
    ], material = reinforcedConcrete)

    ccHalfLength = planScale * dist((-0.457, 0.246), (-0.321, 0.217)) / 2
    ccHalfWidth = planScale * dist((-0.321, 0.217), (-0.29, 0.341)) / 2
    ccLength2 = planScale * dist((-0.29, 0.341), (-0.385, 0.365))
    ccWidth2 = planScale * dist((-0.385, 0.365), (-0.391, 0.329))
    cornerColumnProfile = [
        (ccHalfLength, -ccHalfWidth),
        (-ccHalfLength, -ccHalfWidth),
        (-ccHalfLength, ccHalfWidth),
        (-ccHalfLength + ccLength2, ccHalfWidth),
        (-ccHalfLength + ccLength2, ccHalfWidth - ccWidth2),
        (ccHalfLength, ccHalfWidth - ccWidth2),
    ]
    cornerColumnType = createColumnType(profile = cornerColumnProfile, material = reinforcedConcrete)
    cornerColumnMirroredType = createColumnType(profile = list(map(lambda p: (-p[0], p[1]), cornerColumnProfile)),
                                                material = reinforcedConcrete)

    icHalfLength = planScale * dist((0.028, -0.59), (0.148, -0.614)) / 2
    innerColumnType = createColumnType(profile = [
        (icHalfLength, -icHalfLength),
        (icHalfLength, icHalfLength),
        (-icHalfLength, icHalfLength),
        (-icHalfLength, -icHalfLength),
    ], material = reinforcedConcrete)

    concrete = createMaterial(texturePath = "./ignore/concrete-2500-mm-architextures.jpg", name = "Concrete")
    slabType = createSlabType(material = concrete)

    glass = createMaterial(opacity = 0.5)
    glassWallType = createWallType(material = glass)

    for level in range(numberOfFloors):
        createLevel(level, level * floorHeight)
        levelPoints = getLevelPoints(level, planPoints, degreesPerFloor)
        levelPointsNext = getLevelPoints(level + 1, planPoints, degreesPerFloor)

        slab = createSlab(levelPoints, level, slabType = slabType)
        centralCore(level, slab, coreRadius)
        perimeterColumns(level, levelPoints, numColumnsZ, numColumnsHalfX,
                         firstColumnSpacingZ, firstColumnSpacingX,
                         planAngle, degreesPerFloor, perimeterColumnType)
        cornerColumns(level, levelPoints, levelPointsNext, planAngle, degreesPerFloor, cornerColumnType, cornerColumnMirroredType)
        innerColumns(level, innerColumnPoints, planAngle, degreesPerFloor, innerColumnType)
        curtainWall(level, levelPoints, glassWallType)
    createLevel(numberOfFloors, numberOfFloors * floorHeight)

    finish()

    end_time = time.time_ns()
    print(f"Time: {(end_time-start_time)/1e6} ms")
