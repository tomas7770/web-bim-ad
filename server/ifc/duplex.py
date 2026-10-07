import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.spatial
import ifcopenshell.api.geometry
import ifcopenshell.api.aggregate
import ifcopenshell.util.shape_builder
import ifcopenshell.util.representation
import numpy
import math
import time
from cayan import rotate, dist
from isenberg import add, scale

def createLevel(i, elevation):
    global model
    global building
    global levels

    storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey", name=f"Level {i}")
    ifcopenshell.api.aggregate.assign_object(model, relating_object=building, products=[storey])
    ifcopenshell.api.geometry.edit_object_placement(model, product=storey)

    levels[i] = {
        "elevation": elevation,
        "storey": storey,
    }

def createWallStraight(path, bottomLevel, thickness = 0.2, material = None):
    p0 = path[0]
    p1 = path[1]
    angle = -math.atan2(p0[1] - p1[1], p0[0] - p1[0]) * 180 / math.pi
    floorHeight = levels[bottomLevel+1]["elevation"] - levels[bottomLevel]["elevation"]
    length = dist(p0, p1)
    wallGeometry = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=length, height=floorHeight, thickness=thickness)

    wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
    matrix = numpy.eye(4)
    matrix[:,3][0:3] = (-length / 2, 0, 0)
    matrix = ifcopenshell.util.placement.rotation(angle, "Z") @ matrix
    matrix[:,3][0:3] += ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, 0)
    ifcopenshell.api.geometry.edit_object_placement(model, product=wall, matrix=matrix)
    ifcopenshell.api.geometry.assign_representation(model, product=wall, representation=wallGeometry)
    ifcopenshell.api.spatial.assign_container(model, relating_structure=levels[bottomLevel]["storey"], products=[wall])
    if material:
        ifcopenshell.api.material.assign_material(model, products=[wall], type="IfcMaterial", material=material)

    return {"element": wall, "storey": levels[bottomLevel]["storey"], "thickness": thickness, "matrix": matrix}

def createWindow(host, posX, posY, sizeX, sizeY):
    openingGeometry = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=sizeX-0.2, height=sizeY-0.2, thickness=host["thickness"]+0.01)
    windowGeometry = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=sizeX-0.2, height=sizeY-0.2, thickness=host["thickness"])

    opening = ifcopenshell.api.root.create_entity(model, ifc_class="IfcOpeningElement")
    ifcopenshell.api.geometry.assign_representation(model, product=opening, representation=openingGeometry)
    matrix = numpy.eye(4)
    matrix[:,3][0:3] = (posX, 0, posY)
    matrix = host["matrix"] @ matrix
    ifcopenshell.api.geometry.edit_object_placement(model, product=opening, matrix=matrix)
    ifcopenshell.api.feature.add_feature(model, feature=opening, element=host["element"])

    window = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWindow")
    ifcopenshell.api.geometry.assign_representation(model, product=window, representation=windowGeometry)
    ifcopenshell.api.geometry.edit_object_placement(model, product=window, matrix=matrix)
    ifcopenshell.api.feature.add_filling(model, opening=opening, element=window)
    ifcopenshell.api.spatial.assign_container(model, products=[window], relating_structure=host["storey"])
    ifcopenshell.api.material.assign_material(model, products=[window], type="IfcMaterial", material=glass)

def createDoor(host, posX, sizeX, sizeY):
    openingGeometry = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=sizeX-0.2, height=sizeY-0.2, thickness=host["thickness"]+0.01)
    doorGeometry = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=sizeX-0.2, height=sizeY-0.2, thickness=host["thickness"])

    opening = ifcopenshell.api.root.create_entity(model, ifc_class="IfcOpeningElement")
    ifcopenshell.api.geometry.assign_representation(model, product=opening, representation=openingGeometry)
    matrix = numpy.eye(4)
    matrix[:,3][0:3] = (posX, 0, 0)
    matrix = host["matrix"] @ matrix
    ifcopenshell.api.geometry.edit_object_placement(model, product=opening, matrix=matrix)
    ifcopenshell.api.feature.add_feature(model, feature=opening, element=host["element"])

    door = ifcopenshell.api.root.create_entity(model, ifc_class="IfcDoor")
    ifcopenshell.api.geometry.assign_representation(model, product=door, representation=doorGeometry)
    ifcopenshell.api.geometry.edit_object_placement(model, product=door, matrix=matrix)
    ifcopenshell.api.feature.add_filling(model, opening=opening, element=door)
    ifcopenshell.api.spatial.assign_container(model, products=[door], relating_structure=host["storey"])
    ifcopenshell.api.material.assign_material(model, products=[door], type="IfcMaterial", material=wood)

def createBeam(line, level, elevation):
    global model
    global builder

    p0 = line[0]
    p1 = line[1]

    beam = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBeam")
    matrix = numpy.eye(4)
    matrix[:,3][0:3] = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, elevation)
    ifcopenshell.api.geometry.edit_object_placement(model, product=beam, matrix=matrix)

    vector = (
        p1[0] - p0[0],
        p1[1] - p0[1],
        0
    )
    length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
    vector = tuple(k / length for k in vector)

    profile = [
        [0.082423, 0],
        [0.082423, 0.009652],
        [0.002921, 0.009652],
        [0.002921, 0.30988 - 0.009652],
        [0.082423, 0.30988 - 0.009652],
        [0.082423, 0.30988],

        [-0.082423, 0.30988],
        [-0.082423, 0.30988 - 0.009652],
        [-0.002921, 0.30988 - 0.009652],
        [-0.002921, 0.009652],
        [-0.082423, 0.009652],
        [-0.082423, 0],

        [0.082423, 0],
    ];
    profile = list(map(lambda p: scale(p, 1000), profile))
    curve = builder.polyline(profile)
    solid = builder.extrude(curve, length * 1000, extrusion_vector=vector)
    geometry = builder.get_representation(
        context=body,
        items=solid
    )

    ifcopenshell.api.geometry.assign_representation(model, product=beam, representation=geometry)
    ifcopenshell.api.spatial.assign_container(model, relating_structure=levels[level]["storey"], products=[beam])

def createSlab(length, width, level, material):
    slabGeometry = ifcopenshell.api.geometry.add_slab_representation(model, context=body, depth=0.2, polyline=[
        (0, 0),
        (0, length),
        (width, length),
        (width, 0),
        (0, 0),
    ])

    slab = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSlab")
    ifcopenshell.api.geometry.edit_object_placement(model, product=slab)
    ifcopenshell.api.geometry.assign_representation(model, product=slab, representation=slabGeometry)
    ifcopenshell.api.spatial.assign_container(model, relating_structure=levels[level]["storey"], products=[slab])
    ifcopenshell.api.material.assign_material(model, products=[slab], type="IfcMaterial", material=material)

    return {"element": slab, "storey": levels[level]["storey"]}

def createOpening(host, posX, posY, sizeX, sizeY):
    openingGeometry = ifcopenshell.api.geometry.add_slab_representation(model, context=body, depth=0.21, polyline=[
        (0, 0),
        (0, sizeY),
        (sizeX, sizeY),
        (sizeX, 0),
    ])

    opening = ifcopenshell.api.root.create_entity(model, ifc_class="IfcOpeningElement")
    ifcopenshell.api.geometry.assign_representation(model, product=opening, representation=openingGeometry)
    matrix = numpy.eye(4)
    matrix[:,3][0:3] = (posX, posY, 0)
    ifcopenshell.api.geometry.edit_object_placement(model, product=opening, matrix=matrix)
    ifcopenshell.api.feature.add_feature(model, feature=opening, element=host["element"])

def createStair(basePoint, direction, bottomLevel):
    stepWidth = 0.91
    stepHeight = 0.19
    stepDepth = 0.25

    slabGeometry = ifcopenshell.api.geometry.add_slab_representation(model, context=body, depth=stepHeight, polyline=[
        (0, 0),
        (0, stepWidth),
        (stepDepth, stepWidth),
        (stepDepth, 0),
        (0, 0),
    ])

    slab = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSlab")
    ifcopenshell.api.geometry.edit_object_placement(model, product=slab)
    ifcopenshell.api.geometry.assign_representation(model, product=slab, representation=slabGeometry)
    ifcopenshell.api.spatial.assign_container(model, relating_structure=levels[level]["storey"], products=[slab])
    ifcopenshell.api.material.assign_material(model, products=[slab], type="IfcMaterial", material=material)

    forward = (direction[0], direction[1])
    forwardLength = dist(forward)
    forward = (direction[0] / forwardLength, direction[1] / forwardLength)

    right = (
        forward.y,
        -forward.x
    )

    height = levels[bottomLevel+1]["elevation"] - levels[bottomLevel]["elevation"]

    steps = math.floor(height / stepHeight)
    for i in range(steps):
        center2D = add(basePoint, scale(forward, stepDepth / 2 + i * stepDepth))
        center2D = add(center2D, scale(right, -stepWidth / 2))

        position = (
            center2D.x,
            center2D.y,
            levels[bottomLevel]["elevation"] + stepHeight / 2 + i * stepHeight,
        )
        angle = math.atan2(direction[0], direction[1]) * 180 / math.pi;

def initMaterials():
    global wood, brick, glass, grass

    wood = ifcopenshell.api.material.add_material(model)
    style = ifcopenshell.api.style.add_style(model)
    ifcopenshell.api.style.add_surface_style(model,
        style=style, ifc_class="IfcSurfaceStyleShading", attributes={
            "SurfaceColour": { "Name": None, "Red": 0.463, "Green": 0.388, "Blue": 0.255 },
        })
    ifcopenshell.api.style.assign_material_style(model, material=wood, style=style, context=body)

    brick = ifcopenshell.api.material.add_material(model)
    style = ifcopenshell.api.style.add_style(model)
    ifcopenshell.api.style.add_surface_style(model,
        style=style, ifc_class="IfcSurfaceStyleShading", attributes={
            "SurfaceColour": { "Name": None, "Red": 0.667, "Green": 0.392, "Blue": 0.412 },
        })
    ifcopenshell.api.style.assign_material_style(model, material=brick, style=style, context=body)

    glass = ifcopenshell.api.material.add_material(model)
    style = ifcopenshell.api.style.add_style(model)
    ifcopenshell.api.style.add_surface_style(model,
        style=style, ifc_class="IfcSurfaceStyleShading", attributes={
            "SurfaceColour": { "Name": None, "Red": 0.75, "Green": 0.75, "Blue": 0.75 },
            "Transparency": 0.5
        })
    ifcopenshell.api.style.assign_material_style(model, material=glass, style=style, context=body)

    grass = ifcopenshell.api.material.add_material(model)
    style = ifcopenshell.api.style.add_style(model)
    ifcopenshell.api.style.add_surface_style(model,
        style=style, ifc_class="IfcSurfaceStyleShading", attributes={
            "SurfaceColour": { "Name": None, "Red": 0.0, "Green": 0.5, "Blue": 0.0 },
        })
    ifcopenshell.api.style.assign_material_style(model, material=grass, style=style, context=body)

def slab(length, width, level):
    return createSlab(length, width, level, wood)

def exteriorWalls(length, width, level):
    extWall0 = createWallStraight([(0, 0), (0, length)], level, thickness = 0.4, material = brick)
    extWall1 = createWallStraight([(0, length), (width, length)], level, thickness = 0.4, material = brick)
    extWall2 = createWallStraight([(width, length), (width, 0)], level, thickness = 0.4, material = brick)
    extWall3 = createWallStraight([(width, 0), (0, 0)], level, thickness = 0.4, material = brick)
    return (extWall0, extWall1, extWall2, extWall3)

def interiorWalls(length, width, level, paths):
    intWallsA = []
    intWallsB = []
    for path in paths:
        intWallsA.append(createWallStraight(path, level, thickness = 0.12))
        symmetricPath = [(width - path[0][0], length - path[0][1]), (width - path[1][0], length - path[1][1])]
        intWallsB.append(createWallStraight(symmetricPath, level, thickness = 0.12))
    return (intWallsA, intWallsB)

def groundFloor(length, width):
    level = 0

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
    createWallStraight([(0, 3.6 + 2.8 + 2.9 + separatorThickness / 2),
                (width / 2 + middleSeparatorThickness / 2, 3.6 + 2.8 + 2.9 + separatorThickness / 2)],
                level,
                thickness = separatorThickness)
    createWallStraight([(width, length - 3.6 - 2.8 - 2.9 - separatorThickness / 2),
                    (width / 2 - middleSeparatorThickness / 2, length - 3.6 - 2.8 - 2.9 - separatorThickness / 2)],
                    level,
                    thickness = separatorThickness)

    # Middle separator
    createWallStraight([(width / 2, 3.6 + 2.8 + 0.6), (width / 2, 3.6 + 2.8 + 2.9)], level,
               thickness = middleSeparatorThickness)

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
    #stairType = createStairType(0.91, 0.19, 0.25, wood)
    #createStair((0.91, 5.57), (0, 1), level, stairType)
    #createStair((width - 0.91, length - 5.57), (0, -1), level, stairType)

def firstFloor(elevation, height, length, width):
    level = 1

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

    createWallStraight([(width / 2, 0), (width / 2, length)], level, thickness = width - 2 * (2 + 1.62))

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
    createSlab(length, width, level, grass) # [0, 0.616, 0]

def gen_duplex_ifc(floor0Height = 3.1, floor1Height = 2.9, length = 17.8, width = 8.8):
    start_time = time.time_ns()

    global model
    global body
    global building
    global levels
    global builder

    model = ifcopenshell.api.project.create_file()
    project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject", name="My Project")
    ifcopenshell.api.unit.assign_unit(model)
    context = ifcopenshell.api.context.add_context(model, context_type="Model")
    body = ifcopenshell.api.context.add_context(model, context_type="Model",
        context_identifier="Body", target_view="MODEL_VIEW", parent=context)
    site = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite", name="My Site")
    building = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding", name=f"Building")
    ifcopenshell.api.aggregate.assign_object(model, relating_object=project, products=[site])
    ifcopenshell.api.aggregate.assign_object(model, relating_object=site, products=[building])
    ifcopenshell.api.geometry.edit_object_placement(model, product=building)
    levels = {}
    builder = ifcopenshell.util.shape_builder.ShapeBuilder(model)

    createLevel(0, 0)
    createLevel(1, floor0Height)
    createLevel(2, floor0Height + floor1Height)

    initMaterials()
    groundFloor(length, width)
    firstFloor(floor0Height, floor1Height, length, width)
    roof(floor0Height + floor1Height, length, width)

    for level in levels.values():
        matrix = numpy.eye(4)
        matrix[:,3][0:3] = (0, 0, level["elevation"])
        ifcopenshell.api.geometry.edit_object_placement(model, product=level["storey"], matrix=matrix, should_transform_children=True)

    end_time = time.time_ns()
    print(f"Generated model in {(end_time-start_time)/1e6} ms")

    return model.to_string()
