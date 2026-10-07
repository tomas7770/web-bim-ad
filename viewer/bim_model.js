// Xeokit
import {
    Viewer,
    SceneModel,
    buildBoxGeometry,
    Mesh,
    PhongMaterial,
    ReadableGeometry,
    buildPlaneGeometry,
} from "./xeokit-sdk.min.es.js";

// ThatOpen
import * as THREE from "three";
import * as WEBIFC from "web-ifc";
import * as FRAGS from "@thatopen/fragments";
import { degToRad } from "three/src/math/MathUtils.js";

const api = new WEBIFC.IfcAPI();
api.SetWasmPath("https://unpkg.com/web-ifc@0.0.77/", true);
await api.Init();
const geometryEngine = new FRAGS.GeometryEngine(api);
//

// W12x26
const defaultBeamProfile = [
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
];

// 300x300 mm
const defaultColumnProfile = [
    [0.15, -0.15],
    [0.15, 0.15],
    [-0.15, 0.15],
    [-0.15, -0.15],
];

let viewer;
let model_i = 0;

let planesVisible = true;

function UUID(uuid) {
    return {uuid: uuid};
}

export function initViewer() {
    viewer = new Viewer({
        canvasId: "xeokit_canvas",
        transparent: true
    });
    return viewer;
}

export function createModel() {
    let model = {
        id: `model${model_i}`,
        sceneModel: new SceneModel(viewer.scene, {
            id: `model${model_i}`,
            isModel: true,
            edges: true,
        }),
        metaObjects: [],
        metaModel: null,

        object_i: 0,
        levels: {},
        levelPlaneMeshes: {},
        materials: {},
        wallTypes: {},
        slabTypes: {},
        beamTypes: {},
        columnTypes: {},
        stairTypes: {},
        walls: {},
        slabs: {},
        roofs: {},
        beams: [],
        columns: {},
        stairs: [],

        dirty: true,
    };

    model.metaObjects.push({
        id: `project_${model.id}`,
        name: `Project`,
        type: "Project",
    });
    model.metaObjects.push({
        id: `site_${model.id}`,
        name: `Site`,
        type: "Site",
        parent: `project_${model.id}`,
    });
    model.metaObjects.push({
        id: `building_${model.id}`,
        name: `Building`,
        type: "Building",
        parent: `site_${model.id}`,
    });

    createMaterial(model, "materialDefault");
    createWallType(model, "wallDefault");
    createSlabType(model, "slabDefault");
    createSlabType(model, "roofDefault", undefined, undefined, "Roof");
    createBeamType(model, "beamDefault");
    createColumnType(model, "columnDefault");
    createStairType(model, "stairDefault");

    model_i += 1;
    return model;
}

export function finalizeModel(model) {
    let startTime = performance.now();
    for (const wall of Object.values(model.walls)) {
        createWallGeometry(model, wall);
    }
    console.log(`Wall + windows/doors geometry time: ${performance.now() - startTime} ms`);

    startTime = performance.now();
    for (const slab of Object.values(model.slabs)) {
        createSlabGeometry(model, slab);
    }
    console.log(`Slab geometry time: ${performance.now() - startTime} ms`);

    startTime = performance.now();
    for (const roof of Object.values(model.roofs)) {
        createSlabGeometry(model, roof);
    }
    console.log(`Roof geometry time: ${performance.now() - startTime} ms`);

    startTime = performance.now();
    for (const beam of model.beams) {
        createBeamGeometry(model, beam);
    }
    console.log(`Beam geometry time: ${performance.now() - startTime} ms`);

    startTime = performance.now();
    for (const column of Object.values(model.columns)) {
        createColumnGeometry(model, column);
    }
    console.log(`Column geometry time: ${performance.now() - startTime} ms`);

    startTime = performance.now();
    for (const stair of model.stairs) {
        createStairGeometry(model, stair);
    }
    console.log(`Stair geometry time: ${performance.now() - startTime} ms`);

    model.sceneModel.finalize();
    model.metaModel = viewer.metaScene.createMetaModel(model.id, {
        metaObjects: model.metaObjects
    });
    model.dirty = false;
}

export function destroyModel(model) {
    if (!model.dirty)
    {
        viewer.metaScene.destroyMetaModel(model.id);
        model.sceneModel.destroy();
    }
    for (const [_, mesh] of Object.entries(model.levelPlaneMeshes)) {
        mesh.destroy();
    }
}

export function createLevel(model, i, elevation, name = null) {
    model.metaObjects.push({
        id: `level${i}_${model.id}`,
        name: name ? name : `Level ${i}`,
        type: "BuildingStorey",
        parent: `building_${model.id}`,
    });
    model.levels[i] = elevation;
    model.levelPlaneMeshes[i] = new Mesh(viewer.scene, {
        geometry: new ReadableGeometry(viewer.scene, buildPlaneGeometry({
            xSize: 10,
            ySize: 10,
            zSize: 10
        })),
        material: new PhongMaterial(viewer.scene, {
            ambient: [0.9, 0.3, 0.9],
            alpha: 0.5,
            backfaces: true,
        }),
        position: [0, elevation, 0],
        collidable: false,
        pickable: false,
        visible: planesVisible,
    });
}

export function togglePlanesVisible() {
    planesVisible = !planesVisible;
    return planesVisible;
}

function generateBoxUVs(sxSize, sySize, szuSize, szvSize) {
    return [
        // v0-v1-v2-v3 front
        sxSize, 0,
        0, 0,
        0, sySize,
        sxSize, sySize,

        // v0-v3-v4-v1 right
        0, 0,
        0, sySize,
        szuSize, sySize,
        szuSize, 0,

        // v0-v1-v6-v1 top
        sxSize, szvSize,
        sxSize, 0,
        0, 0,
        0, szvSize,

        // v1-v6-v7-v2 left
        szuSize, 0,
        0, 0,
        0, sySize,
        szuSize, sySize,

        // v7-v4-v3-v2 bottom
        0, szvSize,
        sxSize, szvSize,
        sxSize, 0,
        0, 0,

        // v4-v7-v6-v1 back
        0, sySize,
        sxSize, sySize,
        sxSize, 0,
        0, 0
    ];
}

function generateUVs(geometry, indexArray, positions, normals, matXScale, matYScale) {
    const uvArray = new Float32Array((positions.length / 3) * 2);

    for (let i = 0; i < indexArray.length; i++) {
        const index = indexArray[i];
        const x = positions[index * 3];
        const y = positions[index * 3 + 1];
        const z = positions[index * 3 + 2];

        const nx1 = normals[index * 3];
        const ny1 = normals[index * 3 + 1];
        const nz1 = normals[index * 3 + 2];

        const absNx = Math.abs(nx1);
        const absNy = Math.abs(ny1);
        const absNz = Math.abs(nz1);

        if (absNx > absNy && absNx > absNz) {
            // Use x direction
            uvArray[index * 2] = y / matYScale;
            uvArray[index * 2 + 1] = z / matXScale;
        } else if (absNy > absNx && absNy > absNz) {
            // Use y direction
            uvArray[index * 2] = x / matXScale;
            uvArray[index * 2 + 1] = z / matYScale;
        } else {
            // Use z direction
            uvArray[index * 2] = x / matXScale;
            uvArray[index * 2 + 1] = y / matYScale;
        }
    }

    const attr = new THREE.BufferAttribute(uvArray, 2);
    attr.onUpload(function callback(thisObj) {
        delete thisObj.array;
    });

    geometry.setAttribute("uv", attr);
}

export function createWallType(model, wallTypeId, thickness = 0.2, materialId = "materialDefault", name = "Wall") {
    model.wallTypes[wallTypeId] = {
        thickness: thickness,
        materialId: materialId,
        name: name,
        attributes: {
            Thickness: thickness + "m",
            Material: UUID(materialId),
        },
    };
}

export function createSlabType(model, slabTypeId, thickness = 0.2, materialId = "materialDefault", name = "Slab") {
    model.slabTypes[slabTypeId] = {
        thickness: thickness,
        materialId: materialId,
        name: name,
        attributes: {
            Thickness: thickness + "m",
            Material: UUID(materialId),
        },
    };
}

export function createBeamType(model, beamTypeId, profile = defaultBeamProfile, materialId = "materialDefault", name = "Beam") {
    model.beamTypes[beamTypeId] = {
        profile: profile,
        materialId: materialId,
        name: name,
        attributes: {
            Profile: profile,
            Material: UUID(materialId),
        },
    };
}

export function createColumnType(model, columnTypeId, profile = defaultColumnProfile, materialId = "materialDefault", name = "Column") {
    model.columnTypes[columnTypeId] = {
        profile: profile,
        materialId: materialId,
        name: name,
        attributes: {
            Profile: profile,
            Material: UUID(materialId),
        },
    };
}

export function createStairType(model, stairTypeId, width = 1, height = 0.18, depth = 0.28, materialId = "materialDefault", name = "Stair") {
    model.stairTypes[stairTypeId] = {
        width: width,
        height: height,
        depth: depth,
        materialId: materialId,
        name: name,
        attributes: {
            Width: width + "m",
            Height: height + "m",
            Depth: depth + "m",
            Material: UUID(materialId),
        },
    };
}


export function createWall(model, wallId, path, bottomLevel, opt) {
    let wallTypeId = opt ? opt.wallTypeId : null;
    wallTypeId = wallTypeId ? wallTypeId : "wallDefault";
    let wallType = model.wallTypes[wallTypeId];
    if (!wallType) throw new Error("Given wall type does not exist");
    const topLevel = opt ? opt.topLevel : null;
    const height = opt ? opt.height : null;
    const copyUuid = opt ? opt.copyUuid : null;

    const parentId = `level${bottomLevel}_${model.id}`;
    model.metaObjects.push({
        id: `wall${model.object_i}_${model.id}`,
        name: wallType.name,
        type: "Wall",
        parent: parentId,
        attributes: {
            "Type": UUID(wallTypeId),
        },
    });

    model.walls[wallId] = {
        object_i: model.object_i,
        parentId: parentId,
        path: path,
        bottomLevel: bottomLevel,
        topLevel: topLevel,
        height: height,
        thickness: wallType.thickness,
        material: model.materials[wallType.materialId],
        openings: [],
        windows: new Map(),
        doors: new Map(),
        copyUuid: copyUuid,
    };

    model.object_i += 1;
}

function getWallMatrix(position, angle) {
    return new THREE.Matrix4().compose(
        new THREE.Vector3(position[0], position[1], position[2]),
        new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), angle * Math.PI / 180),
        new THREE.Vector3(1, 1, 1)
    );
}

function addSweepCaps(geometry) {

    const positionAttr = geometry.getAttribute("position");
    const normalAttr = geometry.getAttribute("normal");
    const indexAttr = geometry.getIndex();

    const positions = Array.from(positionAttr.array);
    const normals = Array.from(normalAttr.array);
    const indices = Array.from(indexAttr.array);

    const startVerts = [20, 2, 1, 7];
    const end = indices.length;
    const endVerts   = [end - 2, end - 3, end - 9, end - 15];

    function addCap(vertexIndices, reverse) {

        const baseIndex = positions.length / 3;

        // ----- Compute face normal -----

        const a = new THREE.Vector3().fromBufferAttribute(positionAttr, vertexIndices[0]);
        const b = new THREE.Vector3().fromBufferAttribute(positionAttr, vertexIndices[1]);
        const d = new THREE.Vector3().fromBufferAttribute(positionAttr, vertexIndices[3]);

        const normal = new THREE.Vector3()
            .subVectors(b, a)
            .cross(new THREE.Vector3().subVectors(d, a))
            .normalize();

        if (reverse)
            normal.negate();

        // ----- Duplicate vertices -----

        for (let i = 0; i < 4; i++) {

            const v = vertexIndices[i];

            positions.push(
                positionAttr.getX(v),
                positionAttr.getY(v),
                positionAttr.getZ(v)
            );

            normals.push(
                normal.x,
                normal.y,
                normal.z
            );
        }

        if (!reverse) {

            indices.push(
                baseIndex + 0,
                baseIndex + 1,
                baseIndex + 2,

                baseIndex + 0,
                baseIndex + 2,
                baseIndex + 3
            );

        } else {

            indices.push(
                baseIndex + 0,
                baseIndex + 2,
                baseIndex + 1,

                baseIndex + 0,
                baseIndex + 3,
                baseIndex + 2
            );

        }

    }

    addCap(startVerts, true);
    addCap(endVerts, false);

    geometry.setAttribute(
        "position",
        new THREE.Float32BufferAttribute(positions, 3)
    );

    geometry.setAttribute(
        "normal",
        new THREE.Float32BufferAttribute(normals, 3)
    );

    geometry.setIndex(indices);

    geometry.attributes.position.needsUpdate = true;
    geometry.attributes.normal.needsUpdate = true;
}

function createWallGeometry(model, wall) {
    let position, angle;
    let geometryPositions, geometryNormals, geometryIndices, geometryUV;

    const path = wall.path;
    const thickness = wall.thickness;
    const material = wall.material;
    if (!material) throw new Error("Given material does not exist");

    let height;
    if (wall.height) {
        height = wall.height;
    }
    else if (wall.topLevel) {
        height = model.levels[wall.topLevel] - model.levels[wall.bottomLevel];
    }
    else if (model.levels[wall.bottomLevel + 1]) {
        height = model.levels[wall.bottomLevel + 1] - model.levels[wall.bottomLevel];
    }
    else {
        height = 3;
    }

    let geometryId;

    if (path.length == 2) {
        const p0 = path[0];
        const p1 = path[1];
        position = [
            (p0.x + p1.x) / 2,
            model.levels[wall.bottomLevel] + height / 2,
            (p0.z + p1.z) / 2
        ];
        angle = -Math.atan2(p0.z - p1.z, p0.x - p1.x) * 180 / Math.PI;

        const xSize = Math.sqrt((p0.x - p1.x)*(p0.x - p1.x) + (p0.z - p1.z)*(p0.z - p1.z));
        const ySize = height;
        const zSize = thickness;

        if (wall.copyUuid) {
            const copyWall = model.walls[wall.copyUuid];
            if (!copyWall) throw new Error("Given wall copy UUID does not exist");
            geometryId = copyWall.geometryId;
            wall.geometryId = geometryId;
            for (const opening of wall.openings) {
                const holeMatrix = new THREE.Matrix4().makeTranslation(
                    -(-xSize / 2 + opening.sizeX / 2 + opening.posX),
                    -ySize / 2 + opening.sizeY / 2 + opening.posY,
                    0
                );
                if (wall.windows.get(opening)) {
                    createWindowGeometry(model, wall.windows.get(opening), opening, thickness,
                        getWallMatrix(position, angle).multiply(holeMatrix).elements);
                }
            }
        }
        else if (wall.openings.length > 0) {
            const fullBox = new THREE.BoxGeometry(
                xSize,
                ySize,
                zSize
            );
            const wallMesh = new THREE.Mesh(fullBox);

            const holeMeshes = [];
            for (const opening of wall.openings) {
                const holeBox = new THREE.BoxGeometry(
                    opening.sizeX,
                    opening.sizeY,
                    thickness
                );
                const holeMesh = new THREE.Mesh(holeBox);
                holeMesh.position.set(
                    -(-xSize / 2 + opening.sizeX / 2 + opening.posX),
                    -ySize / 2 + opening.sizeY / 2 + opening.posY,
                    0
                );
                holeMesh.updateMatrixWorld(true);
                holeMeshes.push(holeMesh);

                if (wall.windows.get(opening)) {
                    createWindowGeometry(model, wall.windows.get(opening), opening, thickness,
                        getWallMatrix(position, angle).multiply(holeMesh.matrix).elements);
                }
                if (wall.doors.get(opening)) {
                    createDoorGeometry(model, wall.doors.get(opening), opening, thickness,
                        getWallMatrix(position, angle).multiply(holeMesh.matrix).elements);
                }
            }

            const geometry = new THREE.BufferGeometry();
            geometryEngine.getBooleanOperation(geometry, {
                target: wallMesh,
                operands: holeMeshes,
                type: "DIFFERENCE",
            });

            geometryIndices = geometry.getIndex().array;
            geometryPositions = geometry.getAttribute( 'position' ).array;
            geometryNormals = geometry.getAttribute( 'normal' ).array;

            if (material.textureSetId) {
                generateUVs(geometry, geometryIndices, geometryPositions, geometryNormals, material.xScale, material.yScale);
                geometryUV = geometry.getAttribute( 'uv' ).array;
            }
        }
        else {
            // Simple box
            const box = buildBoxGeometry({
                xSize: xSize / 2,
                ySize: ySize / 2,
                zSize: zSize / 2
            });
    
            const sxSize = xSize / material.xScale;
            const sySize = ySize / material.yScale;
            const szuSize = zSize / material.xScale;
            const szvSize = zSize / material.yScale;
    
            geometryPositions = box.positions;
            geometryNormals = box.normals;
            geometryIndices = box.indices;
            geometryUV = generateBoxUVs(sxSize, sySize, szuSize, szvSize);
        }
    }
    else {
        // Generic path (sweep)
        position = [0, 0, 0];
        angle = 0;

        const geometry = new THREE.BufferGeometry();
        const curvePoints = [];
        for (const point of path) {
            curvePoints.push(point.x);
            curvePoints.push(model.levels[wall.bottomLevel]);
            curvePoints.push(point.z);
        }

        const close = path[0].x == path[path.length - 1].x && path[0].z == path[path.length - 1].z;
        let profilePoints;
        if (close) {
            profilePoints = [
                0, 0, 0,
                thickness, 0, 0,
                thickness, height, 0,
                0, height, 0,
                0, 0, 0,
            ];
        }
        else {
            profilePoints = [
                -thickness/2, 0, 0,
                thickness/2, 0, 0,
                thickness/2, height, 0,
                -thickness/2, height, 0,
                -thickness/2, 0, 0,
            ];
        }

        const sweepData = {
            profilePoints: profilePoints,
            curvePoints: curvePoints,
            startNormal: [0, 1, 0],
            close: close,
        };
        geometryEngine.getSweep(geometry, sweepData);
        if (!close) {
            addSweepCaps(geometry);
        }

        geometryIndices = geometry.getIndex().array;
        geometryPositions = geometry.getAttribute( 'position' ).array;
        geometryNormals = geometry.getAttribute( 'normal' ).array;

        if (material.textureSetId) {
            generateUVs(geometry, geometryIndices, geometryPositions, geometryNormals, material.xScale, material.yScale);
            geometryUV = geometry.getAttribute( 'uv' ).array;
        }
    }

    if (!geometryId) {
        geometryId = `wallGeometry${wall.object_i}_${model.id}`;
        wall.geometryId = geometryId;
        model.sceneModel.createGeometry({
            id: geometryId,
            primitive: "triangles",
            positions: geometryPositions,
            normals: geometryNormals,
            indices: geometryIndices,
            uv: geometryUV,
        });
    }

    model.sceneModel.createMesh({
        id: `wallMesh${wall.object_i}_${model.id}`,
        geometryId: geometryId,
        position: position,
        rotation: [0, angle, 0],
        color: material.albedo,
        opacity: material.opacity,
        textureSetId: material.textureSetId,
    });
    model.sceneModel.createEntity({
        id: `wall${wall.object_i}_${model.id}`,
        meshIds: [
            `wallMesh${wall.object_i}_${model.id}`,
        ],
        parentId: wall.parentId,
        isObject: true,
    });
}

export function createSlab(model, slabId, region, level, opt) {
    let slabTypeId = opt ? opt.slabTypeId : null;
    slabTypeId = slabTypeId ? slabTypeId : "slabDefault";
    let slabType = model.slabTypes[slabTypeId];
    if (!slabType) throw new Error("Given slab type does not exist");

    const parentId = `level${level}_${model.id}`;
    model.metaObjects.push({
        id: `slab${model.object_i}_${model.id}`,
        name: slabType.name,
        type: "Slab",
        parent: parentId,
        attributes: {
            "Type": UUID(slabTypeId),
        },
    });

    model.slabs[slabId] = {
        object_i: model.object_i,
        parentId: parentId,
        region: region,
        level: level,
        thickness: slabType.thickness,
        material: model.materials[slabType.materialId],
        openings: [],
        openingsPoly: [],
    };

    model.object_i += 1;
}

function createSlabGeometry(model, slab) {
    let position;
    let geometryPositions, geometryNormals, geometryIndices, geometryUV;

    const region = slab.region;
    const thickness = slab.thickness;
    const material = slab.material;
    if (!material) throw new Error("Given material does not exist");

    if (Array.isArray(region)) {
        // Generic slab
        position = [0, 0, 0];

        let geometry = new THREE.BufferGeometry();
        const profilePoints = [];
        for (const point of region) {
            profilePoints.push(point.x);
            profilePoints.push(model.levels[slab.level]);
            profilePoints.push(point.z);
        }

        geometryEngine.getExtrusion(geometry, {
            profilePoints: profilePoints,
            direction: [0, slab.isRoof ? 1 : -1, 0],
            cap: true,
            length: thickness,
        });

        if (slab.openingsPoly.length > 0) {
            const slabMesh = new THREE.Mesh(geometry);

            const holeMeshes = [];
            for (const region of slab.openingsPoly) {
                const profilePoints = [];
                for (const point of region) {
                    profilePoints.push(point[0]);
                    profilePoints.push(model.levels[slab.level]);
                    profilePoints.push(point[1]);
                }

                geometry = new THREE.BufferGeometry();
                geometryEngine.getExtrusion(geometry, {
                    profilePoints: profilePoints,
                    direction: [0, slab.isRoof ? 1 : -1, 0],
                    cap: true,
                    length: thickness,
                });

                const holeMesh = new THREE.Mesh(geometry);
                holeMeshes.push(holeMesh);
            }

            geometry = new THREE.BufferGeometry();
            geometryEngine.getBooleanOperation(geometry, {
                target: slabMesh,
                operands: holeMeshes,
                type: "DIFFERENCE",
            });
        }

        geometryIndices = geometry.getIndex().array;
        geometryPositions = geometry.getAttribute( 'position' ).array;
        geometryNormals = geometry.getAttribute( 'normal' ).array;

        if (material.textureSetId) {
            generateUVs(geometry, geometryIndices, geometryPositions, geometryNormals, material.xScale, material.yScale);
            geometryUV = geometry.getAttribute( 'uv' ).array;
        }
    }
    else {
        // Slab rect
        position = [
            (region.start.x + region.end.x) / 2,
            model.levels[slab.level] - thickness / 2 + 0.001,
            (region.start.z + region.end.z) / 2
        ];

        const xSize = Math.abs(region.start.x - region.end.x);
        const ySize = thickness;
        const zSize = Math.abs(region.start.z - region.end.z);

        if (slab.openings.length > 0) {
            const fullBox = new THREE.BoxGeometry(
                xSize,
                ySize,
                zSize
            );
            const slabMesh = new THREE.Mesh(fullBox);

            const holeMeshes = [];
            for (const opening of slab.openings) {
                const holeBox = new THREE.BoxGeometry(
                    opening.sizeX,
                    thickness,
                    opening.sizeY
                );
                const holeMesh = new THREE.Mesh(holeBox);
                holeMesh.position.set(
                    -xSize / 2 + opening.sizeX / 2 + opening.posX,
                    0,
                    -zSize / 2 + opening.sizeY / 2 + opening.posY
                );
                holeMesh.updateMatrixWorld(true);
                holeMeshes.push(holeMesh);
            }

            const geometry = new THREE.BufferGeometry();
            geometryEngine.getBooleanOperation(geometry, {
                target: slabMesh,
                operands: holeMeshes,
                type: "DIFFERENCE",
            });

            geometryIndices = geometry.getIndex().array;
            geometryPositions = geometry.getAttribute( 'position' ).array;
            geometryNormals = geometry.getAttribute( 'normal' ).array;

            if (material.textureSetId) {
                generateUVs(geometry, geometryIndices, geometryPositions, geometryNormals, material.xScale, material.yScale);
                geometryUV = geometry.getAttribute( 'uv' ).array;
            }
        }
        else {
            const box = buildBoxGeometry({
                xSize: xSize / 2,
                ySize: ySize / 2,
                zSize: zSize / 2
            });
    
            const sxSize = xSize / material.xScale;
            const sySize = ySize / material.yScale;
            const szuSize = zSize / material.xScale;
            const szvSize = zSize / material.yScale;
    
            geometryPositions = box.positions;
            geometryNormals = box.normals;
            geometryIndices = box.indices;
            geometryUV = generateBoxUVs(sxSize, sySize, szuSize, szvSize);
        }
    }

    const geometryId = `slabGeometry${slab.object_i}_${model.id}`;
    model.sceneModel.createGeometry({
        id: geometryId,
        primitive: "triangles",
        positions: geometryPositions,
        normals: geometryNormals,
        indices: geometryIndices,
        uv: geometryUV,
    });

    model.sceneModel.createMesh({
        id: `slabMesh${slab.object_i}_${model.id}`,
        geometryId: geometryId,
        position: position,
        color: material.albedo,
        opacity: material.opacity,
        textureSetId: material.textureSetId,
    });
    model.sceneModel.createEntity({
        id: `slab${slab.object_i}_${model.id}`,
        meshIds: [
            `slabMesh${slab.object_i}_${model.id}`,
        ],
        parentId: slab.parentId,
        isObject: true,
    });
}

export function createRoof(model, roofId, region, level, opt) {
    let roofTypeId = opt ? opt.roofTypeId : null;
    roofTypeId = roofTypeId ? roofTypeId : "roofDefault";
    let roofType = model.slabTypes[roofTypeId];
    if (!roofType) throw new Error("Given roof type does not exist");

    const parentId = `level${level}_${model.id}`;
    model.metaObjects.push({
        id: `slab${model.object_i}_${model.id}`,
        name: roofType.name,
        type: "Roof",
        parent: parentId,
        attributes: {
            "Type": UUID(roofTypeId),
        },
    });

    model.roofs[roofId] = {
        object_i: model.object_i,
        parentId: parentId,
        region: region,
        level: level,
        thickness: roofType.thickness,
        material: model.materials[roofType.materialId],
        openings: [],
        openingsPoly: [],
        isRoof: true,
    };

    model.object_i += 1;
}

export function createBeam(model, line, level, opt) {
    let elevation = opt ? opt.elevation : null;
    elevation = elevation ? elevation : 0;
    let beamTypeId = opt ? opt.beamTypeId : null;
    beamTypeId = beamTypeId ? beamTypeId : "beamDefault";
    let beamType = model.beamTypes[beamTypeId];
    if (!beamType) throw new Error("Given beam type does not exist");

    const parentId = `level${level}_${model.id}`;
    model.metaObjects.push({
        id: `beam${model.object_i}_${model.id}`,
        name: beamType.name,
        type: "Beam",
        parent: parentId,
        attributes: {
            "Type": UUID(beamTypeId),
        },
    });

    model.beams.push({
        object_i: model.object_i,
        parentId: parentId,
        line: line,
        level: level,
        elevation: elevation,
        profile: beamType.profile,
        material: model.materials[beamType.materialId],
    });
    model.object_i += 1;
}

function createBeamGeometry(model, beam) {
    const line = beam.line;
    const elevation = beam.elevation;
    const profile = beam.profile;
    const material = beam.material;
    if (!material) throw new Error("Given material does not exist");

    const p0 = line[0];
    const p1 = line[1];
    const angle = -Math.atan2(p0[0] - p1[0], p0[1] - p1[1]);

    const geometry = new THREE.BufferGeometry();
    const profilePoints = [];
    for (const point of profile) {
        profilePoints.push(point[0] * Math.cos(angle) + p0[0]);
        profilePoints.push(model.levels[beam.level] + point[1] + elevation);
        profilePoints.push(point[0] * Math.sin(angle) + p0[1]);
    }

    const length = Math.sqrt(
        (p1[0] - p0[0])*(p1[0] - p0[0]) +
        (p1[1] - p0[1])*(p1[1] - p0[1])
    );
    geometryEngine.getExtrusion(geometry, {
        profilePoints: profilePoints,
        direction: [(p1[0] - p0[0]) / length, 0, (p1[1] - p0[1]) / length],
        cap: true,
        length: length,
    });

    const geometryIndices = geometry.getIndex().array;
    const geometryPositions = geometry.getAttribute( 'position' ).array;
    const geometryNormals = geometry.getAttribute( 'normal' ).array;
    let geometryUV;

    if (material.textureSetId) {
        generateUVs(geometry, geometryIndices, geometryPositions, geometryNormals, material.xScale, material.yScale);
        geometryUV = geometry.getAttribute( 'uv' ).array;
    }

    const geometryId = `beamGeometry${beam.object_i}_${model.id}`;
    model.sceneModel.createGeometry({
        id: geometryId,
        primitive: "triangles",
        positions: geometryPositions,
        normals: geometryNormals,
        indices: geometryIndices,
        uv: geometryUV,
    });

    model.sceneModel.createMesh({
        id: `beamMesh${beam.object_i}_${model.id}`,
        geometryId: geometryId,
        position: [0, 0, 0],
        color: material.albedo,
        opacity: material.opacity,
        textureSetId: material.textureSetId,
    });
    model.sceneModel.createEntity({
        id: `beam${beam.object_i}_${model.id}`,
        meshIds: [
            `beamMesh${beam.object_i}_${model.id}`,
        ],
        parentId: beam.parentId,
        isObject: true,
    });
}

export function createColumn(model, columnId, position, bottomLevel, opt) {
    let columnTypeId = opt ? opt.columnTypeId : null;
    columnTypeId = columnTypeId ? columnTypeId : "columnDefault";
    let columnType = model.columnTypes[columnTypeId];
    if (!columnType) throw new Error("Given column type does not exist");
    const topPosition = opt ? opt.topPosition : null;
    const angle = opt ? opt.angle : null;
    const topLevel = opt ? opt.topLevel : null;
    const copyUuid = opt ? opt.copyUuid : null;

    const parentId = `level${bottomLevel}_${model.id}`;
    model.metaObjects.push({
        id: `column${model.object_i}_${model.id}`,
        name: columnType.name,
        type: "Column",
        parent: parentId,
        attributes: {
            "Type": UUID(columnTypeId),
        },
    });

    model.columns[columnId] = {
        object_i: model.object_i,
        parentId: parentId,
        position: position,
        bottomLevel: bottomLevel,
        topPosition: topPosition,
        angle: angle,
        topLevel: topLevel,
        profile: columnType.profile,
        material: model.materials[columnType.materialId],
        copyUuid: copyUuid,
    };
    model.object_i += 1;
}

function createColumnGeometry(model, column) {
    let geometryPositions, geometryNormals, geometryIndices, geometryUV;

    const position = column.position;
    const profile = column.profile;
    const material = column.material;
    if (!material) throw new Error("Given material does not exist");

    let levelHeightDelta;
    if (column.topLevel) {
        levelHeightDelta = model.levels[column.topLevel] - model.levels[column.bottomLevel];
    }
    else if (model.levels[column.bottomLevel + 1]) {
        levelHeightDelta = model.levels[column.bottomLevel + 1] - model.levels[column.bottomLevel];
    }
    else {
        levelHeightDelta = 3;
    }

    const bottomPosition = new THREE.Vector3(position[0], model.levels[column.bottomLevel], position[1]);
    const topPosition = column.topPosition
        ? new THREE.Vector3(column.topPosition[0], model.levels[column.bottomLevel] + levelHeightDelta, column.topPosition[1])
        : new THREE.Vector3(position[0], model.levels[column.bottomLevel] + levelHeightDelta, position[1]);
    const deltaPosition = topPosition.sub(bottomPosition);
    const deltaPositionNormalized = new THREE.Vector3().copy(deltaPosition).normalize();

    let geometryId;

    if (column.copyUuid) {
        const copyColumn = model.columns[column.copyUuid];
        if (!copyColumn) throw new Error("Given column copy UUID does not exist");
        geometryId = copyColumn.geometryId;
        column.geometryId = geometryId;
    }
    else {
        const geometry = new THREE.BufferGeometry();
        const profilePoints = [];
        const angle = column.angle ? column.angle : 0.0;
        for (const point of profile) {
            let vec = new THREE.Vector3(point[0], 0, point[1]);
            vec = vec.applyAxisAngle(new THREE.Vector3(0, 1, 0), degToRad(angle));
            profilePoints.push(vec.x);
            profilePoints.push(0);
            profilePoints.push(vec.z);
        }
    
        geometryEngine.getExtrusion(geometry, {
            profilePoints: profilePoints,
            direction: [deltaPositionNormalized.x, deltaPositionNormalized.y, deltaPositionNormalized.z],
            cap: true,
            length: deltaPosition.length(),
        });
    
        geometryIndices = geometry.getIndex().array;
        geometryPositions = geometry.getAttribute( 'position' ).array;
        geometryNormals = geometry.getAttribute( 'normal' ).array;
    
        if (material.textureSetId) {
            generateUVs(geometry, geometryIndices, geometryPositions, geometryNormals, material.xScale, material.yScale);
            geometryUV = geometry.getAttribute( 'uv' ).array;
        }
    }

    if (!geometryId) {
        geometryId = `columnGeometry${column.object_i}_${model.id}`;
        column.geometryId = geometryId;
        model.sceneModel.createGeometry({
            id: geometryId,
            primitive: "triangles",
            positions: geometryPositions,
            normals: geometryNormals,
            indices: geometryIndices,
            uv: geometryUV,
        });
    }

    model.sceneModel.createMesh({
        id: `columnMesh${column.object_i}_${model.id}`,
        geometryId: geometryId,
        position: [position[0], model.levels[column.bottomLevel], position[1]],
        color: material.albedo,
        opacity: material.opacity,
        textureSetId: material.textureSetId,
    });
    model.sceneModel.createEntity({
        id: `column${column.object_i}_${model.id}`,
        meshIds: [
            `columnMesh${column.object_i}_${model.id}`,
        ],
        parentId: column.parentId,
        isObject: true,
    });
}

export function createMaterial(model, materialId, albedo = [0.75, 0.75, 0.75], opacity = 1.0,
    xScale = 1, yScale = 1,
    textureUrl = null, name = "Unnamed Material") {

    if (textureUrl) {
        model.sceneModel.createTexture({
            id: `texture${materialId}_${model.id}`,
            src: textureUrl,
        });

        model.sceneModel.createTextureSet({
            id: `textureSet${materialId}_${model.id}`,
            colorTextureId: `texture${materialId}_${model.id}`,
        });
    }

    model.materials[materialId] = {
        albedo: albedo,
        opacity: opacity,
        xScale: xScale,
        yScale: yScale,
        textureSetId: textureUrl ? `textureSet${materialId}_${model.id}` : null,
        name: name,
        attributes: {
            Albedo: albedo,
            Opacity: opacity,
            Texture: textureUrl ? textureUrl : "None",
            "Texture X Scale": xScale,
            "Texture Y Scale": yScale,
        },
    };
}

export function createOpening(model, hostId, posX, posY, sizeX, sizeY) {
    const opening = {
        posX: posX,
        posY: posY,
        sizeX: sizeX,
        sizeY: sizeY,
    };
    if (model.walls[hostId]) {
        model.walls[hostId].openings.push(opening);
    }
    else if (model.slabs[hostId]) {
        model.slabs[hostId].openings.push(opening);
    }
    return opening;
}

export function createOpeningPoly(model, hostId, region) {
    if (model.slabs[hostId]) {
        model.slabs[hostId].openingsPoly.push(region);
    }
    else if (model.roofs[hostId]) {
        model.roofs[hostId].openingsPoly.push(region);
    }
    return region;
}

function createElementInOpening(model, host, opening, elementsContainer, name, type) {
    const object_i = model.object_i++;
    const element = {
        object_i: object_i,
        id: `element${object_i}_${model.id}`,
        parentId: host.parentId,
    }
    model.metaObjects.push({
        id: element.id,
        name: name,
        type: type,
        parent: element.parentId,
    });
    elementsContainer.set(opening, element);
}

export function createWindow(model, wallId, opening) {
    createElementInOpening(model, model.walls[wallId], opening, model.walls[wallId].windows, "Window", "Window");
}

export function createDoor(model, wallId, opening) {
    createElementInOpening(model, model.walls[wallId], opening, model.walls[wallId].doors, "Door", "Door");
}

function createElementInOpeningGeometry(model, element, opening, thickness, matrix, color, opacity) {
    const box = buildBoxGeometry({
        xSize: opening.sizeX / 2,
        ySize: opening.sizeY / 2,
        zSize: thickness / 2
    });

    const geometryId = `elementGeometry${element.object_i}_${model.id}`;
    model.sceneModel.createGeometry({
        id: geometryId,
        primitive: "triangles",
        positions: box.positions,
        normals: box.normals,
        indices: box.indices,
    });
    model.sceneModel.createMesh({
        id: `elementMesh${element.object_i}_${model.id}`,
        geometryId: geometryId,
        matrix: matrix,
        color: color,
        opacity: opacity,
    });
    model.sceneModel.createEntity({
        id: element.id,
        meshIds: [
            `elementMesh${element.object_i}_${model.id}`,
        ],
        parentId: element.parentId,
        isObject: true,
    });
}

function createWindowGeometry(model, window, opening, thickness, matrix) {
    createElementInOpeningGeometry(model, window, opening, thickness, matrix, [0.75, 0.75, 0.75], 0.5);
}

function createDoorGeometry(model, door, opening, thickness, matrix) {
    createElementInOpeningGeometry(model, door, opening, thickness, matrix, [0.3, 0.2, 0.15], 1.0);
}

export function createStair(model, basePoint, direction, bottomLevel, opt) {
    let stairTypeId = opt ? opt.stairTypeId : null;
    stairTypeId = stairTypeId ? stairTypeId : "stairDefault";
    let stairType = model.stairTypes[stairTypeId];
    if (!stairType) throw new Error("Given stair type does not exist");

    let topLevel = opt ? opt.topLevel : null;
    topLevel = topLevel ? topLevel : bottomLevel + 1;

    const parentId = `level${bottomLevel}_${model.id}`;
    model.metaObjects.push({
        id: `stair${model.object_i}_${model.id}`,
        name: stairType.name,
        type: "Stair",
        parent: parentId,
        attributes: {
            "Type": UUID(stairTypeId),
        },
    });

    model.stairs.push({
        object_i: model.object_i,
        parentId: parentId,
        basePoint: basePoint,
        direction: direction,
        bottomLevel: bottomLevel,
        topLevel: topLevel,
        stepWidth: stairType.width,
        stepHeight: stairType.height,
        stepDepth: stairType.depth,
        material: model.materials[stairType.materialId],
    });
    model.object_i += 1;
}

function createStairGeometry(model, stair) {
    const basePoint = stair.basePoint;
    const direction = stair.direction;
    const material = stair.material;
    if (!material) throw new Error("Given material does not exist");

    const forward = new THREE.Vector2(direction[0], direction[1]).normalize();
    // Perpendicular vector (right side)
    const right = new THREE.Vector2(
        forward.y,
        -forward.x
    );

    let height;
    if (model.levels[stair.topLevel]) {
        height = model.levels[stair.topLevel] - model.levels[stair.bottomLevel];
    }
    else {
        height = 3;
    }

    const meshes = [];

    const steps = Math.floor(height / stair.stepHeight);
    for (let i = 0; i < steps; i++) {
        const center2D = new THREE.Vector2(basePoint[0], basePoint[1])
            .addScaledVector(
                forward,
                stair.stepDepth / 2 + i * stair.stepDepth
            )
            .addScaledVector(
                right,
                -stair.stepWidth / 2
            );
        const position = [
            center2D.x,
            model.levels[stair.bottomLevel] + stair.stepHeight / 2 + i * stair.stepHeight,
            center2D.y,
        ];
        const angle = Math.atan2(direction[0], direction[1]) * 180 / Math.PI;

        const xSize = stair.stepWidth;
        const ySize = stair.stepHeight;
        const zSize = stair.stepDepth;

        const box = buildBoxGeometry({
            xSize: xSize / 2,
            ySize: ySize / 2,
            zSize: zSize / 2
        });

        const sxSize = xSize / material.xScale;
        const sySize = ySize / material.yScale;
        const szuSize = zSize / material.xScale;
        const szvSize = zSize / material.yScale;

        const geometryPositions = box.positions;
        const geometryNormals = box.normals;
        const geometryIndices = box.indices;
        const geometryUV = generateBoxUVs(sxSize, sySize, szuSize, szvSize);

        const geometryId = `stairGeometry${stair.object_i}_${i}_${model.id}`;
        model.sceneModel.createGeometry({
            id: geometryId,
            primitive: "triangles",
            positions: geometryPositions,
            normals: geometryNormals,
            indices: geometryIndices,
            uv: geometryUV,
        });

        const meshId = `stairMesh${stair.object_i}_${i}_${model.id}`;
        model.sceneModel.createMesh({
            id: meshId,
            geometryId: geometryId,
            position: position,
            rotation: [0, angle, 0],
            color: material.albedo,
            opacity: material.opacity,
            textureSetId: material.textureSetId,
        });

        meshes.push(meshId);
    }

    model.sceneModel.createEntity({
        id: `stair${stair.object_i}_${model.id}`,
        meshIds: meshes,
        parentId: stair.parentId,
        isObject: true,
    });
}
