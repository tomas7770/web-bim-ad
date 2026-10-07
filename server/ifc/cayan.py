import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.api.project
import ifcopenshell.api.spatial
import ifcopenshell.api.geometry
import ifcopenshell.api.aggregate
import ifcopenshell.api.profile
import ifcopenshell.util.shape_builder
import ifcopenshell.util.representation
import numpy
import math
import time

import cayan

def gen_cayan_tower_ifc():
    start_time = time.time_ns()

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

    # Constants/parameters
    scale = 14
    planAngle = 8.8

    numberOfFloors = 73
    degreesPerFloor = 90 / numberOfFloors
    floorHeight = 306 / numberOfFloors

    numColumnsHalfX = 5
    numColumnsZ = 8
    firstColumnSpacingX = cayan.dist((1.425, 1.705), (1.029, 1.591)) * scale
    firstColumnSpacingZ = cayan.dist((1.425, 1.705), (1.492, 1.305)) * scale
    zLength = cayan.dist((1.425, 1.705), (1.849, -0.854)) * scale
    columnSpacingZ = (zLength - firstColumnSpacingZ * 2) / (numColumnsZ - 1)
    halfXLength = cayan.dist((1.425, 1.705), (0.195, 1.263)) * scale
    columnSpacingX = (halfXLength - firstColumnSpacingX) / (numColumnsHalfX - 1)

    coreRadius = 0.575 * scale

    planPoints = [
        (-1.862, 1.146),
        (-1.44, -1.414),
        (0.247, -1.392),
        (1.849, -0.854),
        (1.425, 1.705),
        (-0.195, 1.263),
    ]
    planPoints = list(map(lambda p: (p[0] * scale, p[1] * scale), planPoints))
    center = cayan.geometricCenter(planPoints)
    planPoints = list(map(lambda p: (p[0] - center[0], p[1] - center[1]), planPoints))

    innerColumnPoints = [
        (0.925, 0.672),
        (1.01, 0.166),
        (1.095, -0.332),
        (-1.053, 0.338),
        (-0.968, -0.16),
        (-0.886, -0.658),
    ]
    innerColumnPoints = list(map(lambda p: (p[0] * scale, p[1] * scale), innerColumnPoints))
    innerColumnPoints = list(map(lambda p: (p[0] - center[0], p[1] - center[1]), innerColumnPoints))

    pcLength = scale * cayan.dist((-0.058, 0.278), (-0.087, 0.156))
    pcHalfWidth = scale * cayan.dist((-0.058, 0.278), (0.016, 0.256)) / 2
    icHalfLength = 1000 * scale * cayan.dist((0.028, -0.59), (0.148, -0.614)) / 2
    ccHalfLength = 1000 * scale * cayan.dist((-0.457, 0.246), (-0.321, 0.217)) / 2
    ccHalfWidth = 1000 * scale * cayan.dist((-0.321, 0.217), (-0.29, 0.341)) / 2
    ccLength2 = 1000 * scale * cayan.dist((-0.29, 0.341), (-0.385, 0.365))
    ccWidth2 = 1000 * scale * cayan.dist((-0.385, 0.365), (-0.391, 0.329))
    innerColumnProfile = [
        (icHalfLength, -icHalfLength),
        (icHalfLength, icHalfLength),
        (-icHalfLength, icHalfLength),
        (-icHalfLength, -icHalfLength),
        (icHalfLength, -icHalfLength),
    ]
    cornerColumnProfile = [
        (ccHalfLength, -ccHalfWidth),
        (-ccHalfLength, -ccHalfWidth),
        (-ccHalfLength, ccHalfWidth),
        (-ccHalfLength + ccLength2, ccHalfWidth),
        (-ccHalfLength + ccLength2, ccHalfWidth - ccWidth2),
        (ccHalfLength, ccHalfWidth - ccWidth2),
        (ccHalfLength, -ccHalfWidth),
    ]
    cornerColumnMirroredProfile = list(map(lambda p: (-p[0], p[1]), cornerColumnProfile))

    # Create all relevant geometry
    slabGeometry = ifcopenshell.api.geometry.add_slab_representation(model, context=body, depth=0.2, polyline=planPoints + [planPoints[0]])
    slabOpeningGeometry = ifcopenshell.api.geometry.add_slab_representation(model, context=body, depth=0.2, polyline=cayan.circle(coreRadius, 10))
    perimeterColumnGeometry = ifcopenshell.api.geometry.add_slab_representation(model, context=body, depth=floorHeight, polyline=[
        (pcHalfWidth, 0),
        (pcHalfWidth, pcLength),
        (-pcHalfWidth, pcLength),
        (-pcHalfWidth, 0),
        (pcHalfWidth, 0),
    ])
    builder = ifcopenshell.util.shape_builder.ShapeBuilder(model)

    # Materials
    concrete = ifcopenshell.api.material.add_material(model)
    style = ifcopenshell.api.style.add_style(model)
    ifcopenshell.api.style.add_surface_style(model,
        style=style, ifc_class="IfcSurfaceStyleShading", attributes={
            "SurfaceColour": { "Name": None, "Red": 0.75, "Green": 0.75, "Blue": 0.75 },
        })
    ifcopenshell.api.style.assign_material_style(model, material=concrete, style=style, context=body)

    reinforcedConcrete = ifcopenshell.api.material.add_material(model)
    style = ifcopenshell.api.style.add_style(model)
    ifcopenshell.api.style.add_surface_style(model,
        style=style, ifc_class="IfcSurfaceStyleShading", attributes={
            "SurfaceColour": { "Name": None, "Red": 0.5, "Green": 0.5, "Blue": 0.5 },
        })
    ifcopenshell.api.style.assign_material_style(model, material=reinforcedConcrete, style=style, context=body)

    glass = ifcopenshell.api.material.add_material(model)
    style = ifcopenshell.api.style.add_style(model)
    ifcopenshell.api.style.add_surface_style(model,
        style=style, ifc_class="IfcSurfaceStyleShading", attributes={
            "SurfaceColour": { "Name": None, "Red": 0.75, "Green": 0.75, "Blue": 0.75 },
            "Transparency": 0.5
        })
    ifcopenshell.api.style.assign_material_style(model, material=glass, style=style, context=body)

    # Aux
    def createIfcColumn(position, storey, angle):
        column = ifcopenshell.api.root.create_entity(model, ifc_class="IfcColumn")
        matrix = numpy.eye(4)
        matrix = ifcopenshell.util.placement.rotation(-angle, "Z") @ matrix
        matrix[:,3][0:3] = (position[0], position[1], 0)
        ifcopenshell.api.geometry.edit_object_placement(model, product=column, matrix=matrix)
        ifcopenshell.api.geometry.assign_representation(model, product=column, representation=perimeterColumnGeometry)
        ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[column])
        ifcopenshell.api.material.assign_material(model, products=[column], type="IfcMaterial", material=reinforcedConcrete)

    def createIfcColumnSlanted(position, storey, topPosition, profile, angle):
        column = ifcopenshell.api.root.create_entity(model, ifc_class="IfcColumn")
        matrix = numpy.eye(4)
        matrix[:,3][0:3] = (position[0], position[1], 0)
        ifcopenshell.api.geometry.edit_object_placement(model, product=column, matrix=matrix)

        vector = (
            topPosition[0] - position[0],
            topPosition[1] - position[1],
            floorHeight
        )
        length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
        vector = tuple(k / length for k in vector)

        rotatedProfile = list(map(lambda p: cayan.rotate(p, angle), profile))
        curve = builder.polyline(rotatedProfile)
        solid = builder.extrude(curve, length * 1000, extrusion_vector=vector)
        geometry = builder.get_representation(
            context=body,
            items=solid
        )

        ifcopenshell.api.geometry.assign_representation(model, product=column, representation=geometry)
        ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[column])
        ifcopenshell.api.material.assign_material(model, products=[column], type="IfcMaterial", material=reinforcedConcrete)

    for i in range(numberOfFloors):
        height = i * floorHeight

        levelPoints = list(map(lambda p: cayan.rotate(p, -degreesPerFloor * i), planPoints))
        levelPointsNext = list(map(lambda p: cayan.rotate(p, -degreesPerFloor * (i + 1)), planPoints))

        # Storey
        storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey", name=f"Level {i}")
        ifcopenshell.api.aggregate.assign_object(model, relating_object=building, products=[storey])
        ifcopenshell.api.geometry.edit_object_placement(model, product=storey)

        # Slab
        slab = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSlab")
        matrix = numpy.eye(4)
        matrix = ifcopenshell.util.placement.rotation(-degreesPerFloor * i, "Z") @ matrix
        ifcopenshell.api.geometry.edit_object_placement(model, product=slab, matrix=matrix)
        ifcopenshell.api.geometry.assign_representation(model, product=slab, representation=slabGeometry)
        ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[slab])
        ifcopenshell.api.material.assign_material(model, products=[slab], type="IfcMaterial", material=concrete)

        # Slab opening
        if i > 0:
            opening = ifcopenshell.api.root.create_entity(model, ifc_class="IfcOpeningElement")
            ifcopenshell.api.geometry.assign_representation(model, product=opening, representation=slabOpeningGeometry)
            ifcopenshell.api.geometry.edit_object_placement(model, product=opening)
            ifcopenshell.api.feature.add_feature(model, feature=opening, element=slab)

        # Central core wall
        centralCoreWall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        ifcopenshell.api.geometry.edit_object_placement(model, product=centralCoreWall)
        profile = ifcopenshell.api.profile.add_arbitrary_profile_with_voids(model,
                        outer_profile=cayan.circle(coreRadius + 0.2, 10, True),
                        inner_profiles=[cayan.circle(coreRadius, 10, True)])
        solid = builder.extrude(profile, floorHeight * 1000, extrusion_vector=(0, 0, 1))
        geometry = builder.get_representation(
            context=body,
            items=solid
        )
        ifcopenshell.api.geometry.assign_representation(model, product=centralCoreWall, representation=geometry)
        ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[centralCoreWall])

        # Perimeter columns
        for j in range(numColumnsZ):
            createIfcColumn(cayan.lerpDist(levelPoints[3], levelPoints[4], firstColumnSpacingZ + columnSpacingZ * j), storey,
                            -cayan.angleFromVec(cayan.diff(levelPoints[4], levelPoints[3])))
            createIfcColumn(cayan.lerpDist(levelPoints[0], levelPoints[1], firstColumnSpacingZ + columnSpacingZ * j), storey,
                            -cayan.angleFromVec(cayan.diff(levelPoints[1], levelPoints[0])))
        createIfcColumn(levelPoints[2], storey, -planAngle - degreesPerFloor * i)
        createIfcColumn(levelPoints[5], storey, -planAngle - degreesPerFloor * i - 180)
        for j in range(numColumnsHalfX):
            # Bottom of plan
            createIfcColumn(cayan.lerpDist(levelPoints[3], levelPoints[2], firstColumnSpacingX + columnSpacingX * j), storey,
                            -cayan.angleFromVec(cayan.diff(levelPoints[3], levelPoints[2])))
            createIfcColumn(cayan.lerpDist(levelPoints[1], levelPoints[2], firstColumnSpacingX + columnSpacingX * j), storey,
                            -cayan.angleFromVec(cayan.diff(levelPoints[2], levelPoints[1])))

            # Top of plan
            createIfcColumn(cayan.lerpDist(levelPoints[4], levelPoints[5], firstColumnSpacingX + columnSpacingX * j), storey,
                            -cayan.angleFromVec(cayan.diff(levelPoints[5], levelPoints[4])))
            createIfcColumn(cayan.lerpDist(levelPoints[0], levelPoints[5], firstColumnSpacingX + columnSpacingX * j), storey,
                            -cayan.angleFromVec(cayan.diff(levelPoints[0], levelPoints[5])))

        # Corner columns
        createIfcColumnSlanted(levelPoints[0], storey, levelPointsNext[0], cornerColumnMirroredProfile, -planAngle - degreesPerFloor * i)
        createIfcColumnSlanted(levelPoints[1], storey, levelPointsNext[1], cornerColumnProfile, -planAngle - degreesPerFloor * i + 180)
        createIfcColumnSlanted(levelPoints[3], storey, levelPointsNext[3], cornerColumnMirroredProfile, -planAngle - degreesPerFloor * i + 180)
        createIfcColumnSlanted(levelPoints[4], storey, levelPointsNext[4], cornerColumnProfile, -planAngle - degreesPerFloor * i)

        # Inner columns
        for point in innerColumnPoints:
            createIfcColumnSlanted(cayan.rotate(point, -degreesPerFloor * i), storey,
                                   cayan.rotate(point, -degreesPerFloor * (i + 1)),
                                   innerColumnProfile, -planAngle - degreesPerFloor * i)

        # Curtain wall
        curtainWall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        ifcopenshell.api.geometry.edit_object_placement(model, product=curtainWall)
        profile = ifcopenshell.api.profile.add_arbitrary_profile_with_voids(model,
                        outer_profile=levelPoints + [levelPoints[0]],
                        inner_profiles=[list(map(lambda p: (p[0] * 0.99, p[1] * 0.99), levelPoints + [levelPoints[0]]))])
        solid = builder.extrude(profile, floorHeight * 1000, extrusion_vector=(0, 0, 1))
        geometry = builder.get_representation(
            context=body,
            items=solid
        )
        ifcopenshell.api.geometry.assign_representation(model, product=curtainWall, representation=geometry)
        ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[curtainWall])
        ifcopenshell.api.material.assign_material(model, products=[curtainWall], type="IfcMaterial", material=glass)

        # Floor vertical position
        matrix = numpy.eye(4)
        matrix[:,3][0:3] = (0, 0, height)
        ifcopenshell.api.geometry.edit_object_placement(model, product=storey, matrix=matrix, should_transform_children=True)

    end_time = time.time_ns()
    print(f"Generated model in {(end_time-start_time)/1e6} ms")

    return model.to_string()
