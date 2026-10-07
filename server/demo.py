from server import *

import math

region = {"start": (0, 0), "end": (5, 8)}
path = [(0, 0), (5, 0)]

def build():
    global region, path
    createLevel(0, 0)
    createLevel(1, 5)
    createLevel(2, 7)
    createSlab(region, 0)
    createSlab(region, 1)
    createSlab(region, 2)
    createWall(path, 0)
    createWall(path, 1)

def buildBatch():
    build()
    finish()

def circle(radius, angle_inc, closed = False, offset = (0, 0)):
    circle_path = []
    for d in range(0, 360, angle_inc):
        a = d * math.pi / 180
        p = (radius * math.cos(a) + offset[0], radius * math.sin(a) + offset[1])
        circle_path.append(p)
    if closed:
        circle_path.append(circle_path[0]);
    return circle_path

def test():
    ## Levels

    # Level with int elevation
    createLevel(0, 0)

    # Level with float elevation and custom name
    createLevel(1, 3.5, "Float Level")

    # More levels
    createLevel(2, 6)
    createLevel(3, 9)

    ## Slabs (default type)

    # Most basic possible slab
    createSlab(region, 0)

    # Polygonal slab
    createSlab(circle(5, 10), 1)

    ## Walls (default type)

    # Most basic possible wall
    createWall(path, 0)

    # Open curve wall
    createWall([(0, 5), (5, 5), (7, 10)], 0)

    # Closed curve wall
    createWall(circle(5, 10, True), 1)

    ## Materials

    # Empty material
    emptyMaterial = createMaterial()

    # Material with albedo
    albedoMaterial = createMaterial(albedo = (1.0, 0.5, 0))

    # Material with texture
    textureMaterial = createMaterial(texturePath = "./textures/uvGrid2.jpg")

    # Material with scaled texture
    scaledTextureMaterial = createMaterial(texturePath = "./textures/uvGrid2.jpg", xScale = -2, yScale = 0.5)

    # Full material
    fullMaterial = createMaterial(albedo = (1, 0, 0), texturePath = "./textures/uvGrid2.jpg", xScale = 2, yScale = 0.5)

    ## Slab types

    # Empty slab type
    emptySlabType = createSlabType()

    # Full slab type
    fullSlabType = createSlabType(thickness = 1.5, material = scaledTextureMaterial, name = "Custom Slab")

    ## Slabs with custom type

    # Slab with empty type
    createSlab(region, 2, emptySlabType)

    # Rectangular slab with full type
    createSlab({"start": (0, 10), "end": (5, 18)}, 2, fullSlabType)

    # Polygonal slab with full type
    createSlab(circle(5, 10), 3, fullSlabType)

    ## Wall types

    # Empty wall type
    emptyWallType = createWallType()

    # Full wall type
    fullWallType = createWallType(thickness = 0.5, material = scaledTextureMaterial, name = "Custom Wall")

    # Wall types with various materials
    emptyMaterialWallType = createWallType(material = emptyMaterial, name = "Empty Material Wall")
    albedoMaterialWallType = createWallType(material = albedoMaterial)
    textureMaterialWallType = createWallType(material = textureMaterial)
    fullMaterialWallType = createWallType(material = fullMaterial)

    ## Walls with custom type

    # Wall with empty type
    createWall(path, 2, emptyWallType)

    # Straight wall with full type
    createWall([(0, 5), (5, 5)], 2, fullWallType)

    # Curved wall with full type
    createWall([(0, 10), (5, 10), (7, 15)], 2, fullWallType)

    # Walls with various materials
    createWall(path, 3, emptyMaterialWallType)
    createWall([(0, 5), (5, 5)], 3, albedoMaterialWallType)
    createWall([(0, 10), (5, 10)], 3, textureMaterialWallType)
    createWall([(0, 15), (5, 15)], 3, fullMaterialWallType)

def testOpenings():
    ## Levels

    createLevel(0, 0)
    createLevel(1, 6)

    ## Materials

    material = createMaterial(texturePath = "./textures/uvGrid2.jpg")

    ## Slabs

    # Custom slab type
    slabType = createSlabType(thickness = 1, material = material)

    # Rectangular slab (default type)
    rectSlabDefault = createSlab(region, 0)

    # Rectangular slab (custom type)
    rectSlabCustom = createSlab({"start": (0, 10), "end": (5, 18)}, 0, slabType)

    # Polygonal slab (default type)
    polySlabDefault = createSlab(circle(5, 10), 1)

    # Polygonal slab (custom type)
    polySlabCustom = createSlab(circle(5, 10, offset = (0, 15)), 1, slabType)

    ## Walls

    # Custom wall type
    wallType = createWallType(thickness = 0.5, material = material)

    # Straight wall (default type)
    rectWallDefault = createWall(path, 0)

    # Straight wall (custom type)
    rectWallCustom = createWall([(0, 5), (5, 5)], 0, wallType)

    # Curved wall (default type)
    polyWallDefault = createWall(circle(5, 10), 1)

    # Curved wall (custom type)
    polyWallCustom = createWall(circle(5, 10, offset = (0, 15)), 1, wallType)

    ## Openings

    # Rectangular opening in rectangular slabs
    createOpening(rectSlabDefault, 0.5, 1, 1.5, 1)
    createOpening(rectSlabCustom, 0.5, 1, 1.5, 1)

    # Rectangular opening in polygonal slabs
    createOpening(polySlabDefault, 0.5, 1, 1.5, 1)
    createOpening(polySlabCustom, 0.5, 1, 1.5, 1)

    # Rectangular opening in straight walls
    createOpening(rectWallDefault, 0.5, 1, 1.5, 1)
    createOpening(rectWallCustom, 0.5, 1, 1.5, 1)

    # Rectangular opening in curved walls
    createOpening(polyWallDefault, 0.5, 1, 1.5, 1)
    createOpening(polyWallCustom, 0.5, 1, 1.5, 1)

    ## Windows and doors

    # Window in straight walls
    createWindow(rectWallDefault, 0.5, 3, 1.5, 1)
    createWindow(rectWallCustom, 0.5, 3, 1.5, 1)

    # Window in curved walls
    createWindow(polyWallDefault, 0.5, 3, 1.5, 1)
    createWindow(polyWallCustom, 0.5, 3, 1.5, 1)

    # Door
    createDoor(rectWallDefault, 2.5, 1.5, 3)
    createDoor(rectWallCustom, 2.5, 1.5, 3)
