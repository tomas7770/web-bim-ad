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

def gen_skyscraper_ifc(floorHeight: float, numberOfFloors: int, length: float, width: float):
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
    exteriorColumnWidth = 0.5 * 1000
    exteriorColumnLength = 0.5 * 1000
    interiorColumnWidth = 0.25 * 1000
    interiorColumnLength = 0.25 * 1000
    interiorColumnThickness = 0.03 * 1000
    interiorColumnFlangeThickness = 0.02 * 1000
    columnLengthDistance = 5
    columnWidthDistance = 5
    floorThickness = 0.3
    stairCaseWidth = 3
    stairCaseLength = 5
    windowHeight = 2
    windowWidth = 1
    roofTopThickness = 0.15

    # Create all relevant geometry
    builder = ifcopenshell.util.shape_builder.ShapeBuilder(model)
    curve = builder.polyline(
        [
            (0, 0),
            (0, exteriorColumnLength),
            (exteriorColumnWidth, exteriorColumnLength),
            (exteriorColumnWidth, 0),
        ]
    )
    solid = builder.extrude(curve, floorHeight * 1000)
    exteriorColumnGeometry = builder.get_representation(
        context=body,
        items=solid
    )

    curve = builder.polyline(
        [
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
        ],
    )
    solid = builder.extrude(curve, floorHeight * 1000)
    interiorColumnGeometry = builder.get_representation(
        context=body,
        items=solid
    )

    slabGeometry = ifcopenshell.api.geometry.add_slab_representation(model, context=body, depth=floorThickness, polyline=[
        (0, 0),
        (0, length),
        (width, length),
        (width, 0),
    ])
    slabOpeningGeometry = ifcopenshell.api.geometry.add_slab_representation(model, context=body, depth=floorThickness, polyline=[
        (0, 0),
        (0, stairCaseLength),
        (stairCaseWidth, stairCaseLength),
        (stairCaseWidth, 0),
    ])

    lengthWallGeometry = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=length, height=floorHeight, thickness=floorThickness)
    widthWallGeometry = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=width, height=floorHeight, thickness=floorThickness)
    openingGeometry = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=windowWidth-0.2, height=windowHeight-0.2, thickness=floorThickness+0.01)
    windowGeometry = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=windowWidth-0.2, height=windowHeight-0.2, thickness=floorThickness)

    stairLengthWallGeometry = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=stairCaseLength, height=floorHeight, thickness=0.2)
    stairWidthWallGeometry = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=stairCaseWidth, height=floorHeight, thickness=0.2)

    roofLengthWallGeometry = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=length, height=windowHeight, thickness=roofTopThickness)
    roofWidthWallGeometry = ifcopenshell.api.geometry.add_wall_representation(model, context=body, length=width, height=windowHeight, thickness=roofTopThickness)

    glass = ifcopenshell.api.material.add_material(model)
    style = ifcopenshell.api.style.add_style(model)
    ifcopenshell.api.style.add_surface_style(model,
        style=style, ifc_class="IfcSurfaceStyleShading", attributes={
            "SurfaceColour": { "Name": None, "Red": 0.75, "Green": 0.75, "Blue": 0.75 },
            "Transparency": 0.5
        })
    ifcopenshell.api.style.assign_material_style(model, material=glass, style=style, context=body)

    interiorColumnPositions = []
    icLengthCount = math.floor(
        length / columnLengthDistance,
    )
    icWidthCount = math.floor(
        width / columnWidthDistance,
    )
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

    extColumnX = width - exteriorColumnWidth / 1000
    extColumnZ = length - exteriorColumnLength / 1000
    exteriorColumnPositions = [
        (0, 0),
        (extColumnX, 0),
        (extColumnX, extColumnZ),
        (0, extColumnZ),
    ]

    for i in range(numberOfFloors):
        height = i * floorHeight

        storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey", name=f"Level {i}")
        ifcopenshell.api.aggregate.assign_object(model, relating_object=building, products=[storey])
        ifcopenshell.api.geometry.edit_object_placement(model, product=storey)

        slab = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSlab")
        ifcopenshell.api.geometry.edit_object_placement(model, product=slab)
        ifcopenshell.api.geometry.assign_representation(model, product=slab, representation=slabGeometry)
        ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[slab])

        if i > 0:
            opening = ifcopenshell.api.root.create_entity(model, ifc_class="IfcOpeningElement")
            ifcopenshell.api.geometry.assign_representation(model, product=opening, representation=slabOpeningGeometry)
            ifcopenshell.api.geometry.edit_object_placement(model, product=opening)
            ifcopenshell.api.feature.add_feature(model, feature=opening, element=slab)

        walls = []

        lengthWall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        matrix = numpy.eye(4)
        matrix = ifcopenshell.util.placement.rotation(90, "Z") @ matrix
        ifcopenshell.api.geometry.edit_object_placement(model, product=lengthWall, matrix=matrix)
        ifcopenshell.api.geometry.assign_representation(model, product=lengthWall, representation=lengthWallGeometry)
        ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[lengthWall])
        walls.append((lengthWall, length, matrix))

        widthWall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        ifcopenshell.api.geometry.edit_object_placement(model, product=widthWall)
        ifcopenshell.api.geometry.assign_representation(model, product=widthWall, representation=widthWallGeometry)
        ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[widthWall])
        walls.append((widthWall, width, numpy.eye(4)))

        lengthWall2 = ifcopenshell.api.root.copy_class(model, product=lengthWall)
        ifcopenshell.api.geometry.assign_representation(model, product=lengthWall2, representation=lengthWallGeometry)
        matrix = numpy.eye(4)
        matrix = ifcopenshell.util.placement.rotation(90, "Z") @ matrix
        matrix[:,3][0:3] = (width, 0, 0)
        ifcopenshell.api.geometry.edit_object_placement(model, product=lengthWall2, matrix=matrix)
        walls.append((lengthWall2, length, matrix))

        widthWall2 = ifcopenshell.api.root.copy_class(model, product=widthWall)
        ifcopenshell.api.geometry.assign_representation(model, product=widthWall2, representation=widthWallGeometry)
        matrix = numpy.eye(4)
        matrix[:,3][0:3] = (0, length, 0)
        ifcopenshell.api.geometry.edit_object_placement(model, product=widthWall2, matrix=matrix)
        walls.append((widthWall2, width, matrix))

        stairLengthWall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        matrix = numpy.eye(4)
        matrix = ifcopenshell.util.placement.rotation(90, "Z") @ matrix
        matrix[:,3][0:3] = (stairCaseWidth, 0, 0)
        ifcopenshell.api.geometry.edit_object_placement(model, product=stairLengthWall, matrix=matrix)
        ifcopenshell.api.geometry.assign_representation(model, product=stairLengthWall, representation=stairLengthWallGeometry)
        ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[stairLengthWall])

        stairWidthWall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        matrix = numpy.eye(4)
        matrix[:,3][0:3] = (0, stairCaseLength, 0)
        ifcopenshell.api.geometry.edit_object_placement(model, product=stairWidthWall, matrix=matrix)
        ifcopenshell.api.geometry.assign_representation(model, product=stairWidthWall, representation=stairWidthWallGeometry)
        ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[stairWidthWall])

        for wall in walls:
            for i in range(math.floor(wall[1] / windowWidth)):
                opening = ifcopenshell.api.root.create_entity(model, ifc_class="IfcOpeningElement")
                ifcopenshell.api.geometry.assign_representation(model, product=opening, representation=openingGeometry)
                matrix = numpy.eye(4)
                matrix[:,3][0:3] = (i * windowWidth + 0.1, 0, 0.1)
                matrix = wall[2] @ matrix
                ifcopenshell.api.geometry.edit_object_placement(model, product=opening, matrix=matrix)
                ifcopenshell.api.feature.add_feature(model, feature=opening, element=wall[0])

                window = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWindow")
                ifcopenshell.api.geometry.assign_representation(model, product=window, representation=windowGeometry)
                ifcopenshell.api.geometry.edit_object_placement(model, product=window, matrix=matrix)
                ifcopenshell.api.feature.add_filling(model, opening=opening, element=window)
                ifcopenshell.api.spatial.assign_container(model, products=[window], relating_structure=storey)
                ifcopenshell.api.material.assign_material(model, products=[window], type="IfcMaterial", material=glass)

        for pos in interiorColumnPositions:
            column = ifcopenshell.api.root.create_entity(model, ifc_class="IfcColumn")
            matrix = numpy.eye(4)
            matrix[:,3][0:3] = (pos[0], pos[1], 0)
            ifcopenshell.api.geometry.edit_object_placement(model, product=column, matrix=matrix)
            ifcopenshell.api.geometry.assign_representation(model, product=column, representation=interiorColumnGeometry)
            ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[column])

        for pos in exteriorColumnPositions:
            column = ifcopenshell.api.root.create_entity(model, ifc_class="IfcColumn")
            matrix = numpy.eye(4)
            matrix[:,3][0:3] = (pos[0], pos[1], 0)
            ifcopenshell.api.geometry.edit_object_placement(model, product=column, matrix=matrix)
            ifcopenshell.api.geometry.assign_representation(model, product=column, representation=exteriorColumnGeometry)
            ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[column])

        matrix = numpy.eye(4)
        matrix[:,3][0:3] = (0, 0, height)
        ifcopenshell.api.geometry.edit_object_placement(model, product=storey, matrix=matrix, should_transform_children=True)

    # Roof
    height = numberOfFloors * floorHeight

    storey = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey", name=f"Level {numberOfFloors}")
    ifcopenshell.api.aggregate.assign_object(model, relating_object=building, products=[storey])
    ifcopenshell.api.geometry.edit_object_placement(model, product=storey)

    roof = ifcopenshell.api.root.create_entity(model, ifc_class="IfcRoof")
    ifcopenshell.api.geometry.edit_object_placement(model, product=roof)
    ifcopenshell.api.geometry.assign_representation(model, product=roof, representation=slabGeometry)
    ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[roof])

    opening = ifcopenshell.api.root.create_entity(model, ifc_class="IfcOpeningElement")
    ifcopenshell.api.geometry.assign_representation(model, product=opening, representation=slabOpeningGeometry)
    ifcopenshell.api.geometry.edit_object_placement(model, product=opening)
    ifcopenshell.api.feature.add_feature(model, feature=opening, element=roof)

    lengthWall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
    matrix = numpy.eye(4)
    matrix = ifcopenshell.util.placement.rotation(90, "Z") @ matrix
    ifcopenshell.api.geometry.edit_object_placement(model, product=lengthWall, matrix=matrix)
    ifcopenshell.api.geometry.assign_representation(model, product=lengthWall, representation=roofLengthWallGeometry)
    ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[lengthWall])
    walls.append((lengthWall, length, matrix))

    widthWall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
    ifcopenshell.api.geometry.edit_object_placement(model, product=widthWall)
    ifcopenshell.api.geometry.assign_representation(model, product=widthWall, representation=roofWidthWallGeometry)
    ifcopenshell.api.spatial.assign_container(model, relating_structure=storey, products=[widthWall])
    walls.append((widthWall, width, numpy.eye(4)))

    lengthWall2 = ifcopenshell.api.root.copy_class(model, product=lengthWall)
    ifcopenshell.api.geometry.assign_representation(model, product=lengthWall2, representation=roofLengthWallGeometry)
    matrix = numpy.eye(4)
    matrix = ifcopenshell.util.placement.rotation(90, "Z") @ matrix
    matrix[:,3][0:3] = (width, 0, 0)
    ifcopenshell.api.geometry.edit_object_placement(model, product=lengthWall2, matrix=matrix)
    walls.append((lengthWall2, length, matrix))

    widthWall2 = ifcopenshell.api.root.copy_class(model, product=widthWall)
    ifcopenshell.api.geometry.assign_representation(model, product=widthWall2, representation=roofWidthWallGeometry)
    matrix = numpy.eye(4)
    matrix[:,3][0:3] = (0, length, 0)
    ifcopenshell.api.geometry.edit_object_placement(model, product=widthWall2, matrix=matrix)
    walls.append((widthWall2, width, matrix))

    matrix = numpy.eye(4)
    matrix[:,3][0:3] = (0, 0, height)
    ifcopenshell.api.geometry.edit_object_placement(model, product=storey, matrix=matrix, should_transform_children=True)
    #

    end_time = time.time_ns()
    print(f"Generated model in {(end_time-start_time)/1e6} ms")

    return model.to_string()
