// Xeokit
import {
    buildSphereGeometry,
    buildGridGeometry,
    TreeViewPlugin,
    DistanceMeasurementsPlugin,
    DistanceMeasurementsMouseControl,
    ContextMenu,
    AxisGizmoPlugin,
    NavCubePlugin,
    Mesh,
    VBOGeometry,
    PhongMaterial,
    FastNavPlugin,
} from "./xeokit-sdk.min.es.js";

// Application
import * as BIM from "./bim_model.js"
import Stats from "three/examples/jsm/libs/stats.module.js";
//

//------------------------------------------------------------------------------------------------------------------
// 1. Create a Viewer,
// 2. Arrange the camera
//------------------------------------------------------------------------------------------------------------------

// 1
const viewer = BIM.initViewer();

// 2
viewer.camera.eye = [-2.56, 8.38, 8.27];
viewer.camera.look = [13.44, 3.31, -14.83];
viewer.camera.up = [0.10, 0.98, -0.14];

viewer.cameraControl.panRightClick = false; // Prevents right-click-drag panning interfering with ContextMenus

//------------------------------------------------------------------------------------------------------------------
// Install FastNavPlugin
//------------------------------------------------------------------------------------------------------------------

const fastNavPlugin = new FastNavPlugin(viewer, {
    hideEdges: true,
    hideColorTexture: false,
});

//------------------------------------------------------------------------------------------------------------------
// Tree view
//------------------------------------------------------------------------------------------------------------------

const treeView = new TreeViewPlugin(viewer, {
    containerElement: document.getElementById("treeViewContainer"),
    autoExpandDepth: 3, // Initially expand tree three storeys deep
    hierarchy: "containment",
    autoAddModels: false,
});
window.treeView = treeView;

const objectContextMenu = new ContextMenu({
    items: [
        [
            {
                title: "Show in Tree",
                doAction: function (context) {
                    const objectId = context.entity.id;
                    context.treeViewPlugin.showNode(objectId);
                    showTreeBar(true);
                }
            }
        ],
        [
            {
                title: "Inspect Properties",
                doAction: function (context) {
                    const objectId = context.entity.id;
                    const metaObject = viewer.metaScene.metaObjects[objectId];
                    //console.log(metaObject);
                    inspectMetaObject(metaObject);
                }
            }
        ],
    ],
    enabled: true
});

const getCanvasPosFromEvent = function (event) {
    const canvasPos = [];
    if (!event) {
        event = window.event;
        canvasPos[0] = event.x;
        canvasPos[1] = event.y;
    } else {
        let element = event.target;
        let totalOffsetLeft = 0;
        let totalOffsetTop = 0;
        let totalScrollX = 0;
        let totalScrollY = 0;
        while (element.offsetParent) {
            totalOffsetLeft += element.offsetLeft;
            totalOffsetTop += element.offsetTop;
            totalScrollX += element.scrollLeft;
            totalScrollY += element.scrollTop;
            element = element.offsetParent;
        }
        canvasPos[0] = event.pageX + totalScrollX - totalOffsetLeft;
        canvasPos[1] = event.pageY + totalScrollY - totalOffsetTop;
    }
    return canvasPos;
};

function handleContextMenu(event) {
    const canvasPos = getCanvasPosFromEvent(event);
    const hit = viewer.scene.pick({
        canvasPos
    });
    if (hit && hit.entity.isObject) {
        objectContextMenu.context = { // Must set context before showing menu
            viewer,
            treeViewPlugin: treeView,
            entity: hit.entity
        };
        objectContextMenu.show(event.pageX, event.pageY);
    }
    event.preventDefault();
}

viewer.scene.canvas.canvas.addEventListener('contextmenu', handleContextMenu);

//------------------------------------------------------------------------------------------------------------------
// Measurements
//------------------------------------------------------------------------------------------------------------------

const distanceMeasurements = new DistanceMeasurementsPlugin(viewer, {});

const distanceMeasurementsMouseControl = new DistanceMeasurementsMouseControl(distanceMeasurements, {});

distanceMeasurementsMouseControl.snapping = true;

const distanceMeasurementsContextMenu = new ContextMenu({
    items: [
        [
            {
                title: "Clear",
                doAction: function (context) {
                    context.distanceMeasurement.destroy();
                }
            },
            {
                getTitle: (context) => {
                    return context.distanceMeasurement.axisVisible ? "Hide Axis" : "Show Axis";
                },
                doAction: function (context) {
                    context.distanceMeasurement.axisVisible = !context.distanceMeasurement.axisVisible;
                }
            },
            {
                getTitle: (context) => {
                    return context.distanceMeasurement.xLabelEnabled && context.distanceMeasurement.labelsVisible ? "Disable X Label" : "Enable X Label";
                },
                doAction: function (context) {
                    context.distanceMeasurement.xLabelEnabled = !context.distanceMeasurement.xLabelEnabled;
                }
            },
            {
                getTitle: (context) => {
                    return context.distanceMeasurement.yLabelEnabled && context.distanceMeasurement.labelsVisible ? "Disable Y Label" : "Enable Y Label";
                },
                doAction: function (context) {
                    context.distanceMeasurement.yLabelEnabled = !context.distanceMeasurement.yLabelEnabled;
                }
            },
            {
                getTitle: (context) => {
                    return context.distanceMeasurement.zLabelEnabled && context.distanceMeasurement.labelsVisible ? "Disable Z Label" : "Enable Z Label";
                },
                doAction: function (context) {
                    context.distanceMeasurement.zLabelEnabled = !context.distanceMeasurement.zLabelEnabled;
                }
            },
            {
                getTitle: (context) => {
                    return context.distanceMeasurement.lengthLabelEnabled && context.distanceMeasurement.labelsVisible ? "Disable Length Label" : "Enable Length Label";
                },
                doAction: function (context) {
                    context.distanceMeasurement.lengthLabelEnabled = !context.distanceMeasurement.lengthLabelEnabled;
                }
            },
            {
                getTitle: (context) => {
                    return context.distanceMeasurement.labelsVisible ? "Hide All Labels" : "Show All Labels";
                },
                doAction: function (context) {
                    context.distanceMeasurement.labelsVisible = !context.distanceMeasurement.labelsVisible;
                }
            },
            {
                getTitle: (context) => {
                    return distanceMeasurementsMouseControl.snapping ? "Disable Snapping" : "Enable Snapping";
                },
                doAction: function (context) {
                    distanceMeasurementsMouseControl.snapping = !distanceMeasurementsMouseControl.snapping;
                }
            },
        ], [
            {
                title: "Clear All",
                getEnabled: function (context) {
                    return (Object.keys(context.distanceMeasurementsPlugin.measurements).length > 0);
                },
                doAction: function (context) {
                    context.distanceMeasurementsPlugin.clear();
                }
            },
            {
                getTitle: () => {
                    return "Cancel Measurement";
                },
                doAction: function () {
                    distanceMeasurementsMouseControl.reset();
                }
            }
        ]
    ]
});

distanceMeasurementsContextMenu.on("hidden", () => {
    if (distanceMeasurementsContextMenu.context.distanceMeasurement) {
        distanceMeasurementsContextMenu.context.distanceMeasurement.setHighlighted(false);
    }
});

distanceMeasurements.on("mouseOver", (e) => {
    e.distanceMeasurement.setHighlighted(true);
});

distanceMeasurements.on("mouseLeave", (e) => {
    if (distanceMeasurementsContextMenu.shown && distanceMeasurementsContextMenu.context.distanceMeasurement.id === e.distanceMeasurement.id) {
        return;
    }
    e.distanceMeasurement.setHighlighted(false);
});

distanceMeasurements.on("contextMenu", (e) => {
    distanceMeasurementsContextMenu.context = { // Must set context before showing menu
        viewer: viewer,
        distanceMeasurementsPlugin: distanceMeasurements,
        distanceMeasurement: e.distanceMeasurement
    };
    distanceMeasurementsContextMenu.show(e.event.clientX, e.event.clientY);
    e.event.preventDefault();
});

// Gizmos
new AxisGizmoPlugin(viewer, {
    canvasId: "myAxisGizmoCanvas"
});

new NavCubePlugin(viewer, {
    canvasId: "myNavCubeCanvas",
    color: "lightblue",
    visible: true,           // Initially visible (default)
    cameraFly: true,       // Fly camera to each selected axis/diagonal
    cameraFlyDuration: 0.5 // How long (in seconds) camera takes to fly to each new axis/diagonal
});

// y=0 plane
const gridPlane = new Mesh(viewer.scene, {
    geometry: new VBOGeometry(viewer.scene, buildGridGeometry({
        size: 100,
        divisions: 20
    })),
    material: new PhongMaterial(viewer.scene, {
        color: [0.0, 0.0, 0.0],
        emissive: [0.4, 0.4, 0.4]
    }),
    position: [0, 0, 0],
    collidable: false,
    pickable: false,
});

// Origin sphere
const originSphere = new Mesh(viewer.scene, {
    geometry: new VBOGeometry(viewer.scene, buildSphereGeometry({
        center: [0, 0, 0],
        radius: 0.2,
    })),
    material: new PhongMaterial(viewer.scene, {
        color: [0.0, 0.0, 0.0],
        emissive: [0.4, 0.4, 0.4]
    }),
    position: [0, 0, 0],
    collidable: false,
    pickable: false,
});

//------------------------------------------------------------------------------------------------------------------
// Create a SceneModel
//------------------------------------------------------------------------------------------------------------------

let model = null;

const modelOps = [];
let batchMode = false;

function parseOp(op) {
    let args = op.split(' ');
    if (args[0]) {
        switch (args[0]) {
        case "BATCH":
            batchMode = true;
            break;
        case "INTERACTIVE":
            batchMode = false;
            break;
        case "FINISH":
            loadModel();
            break;
        case "CLEAR":
            modelOps.length = 0;
            if (!batchMode) {
                loadModel();
            }
            break;
        case "UNDO":
            modelOps.pop();
            if (!batchMode) {
                loadModel();
            }
            break;
        default:
            modelOps.push({op: op, args: args});
            if (!batchMode) {
                loadModel();
            }
            break;
        }
    }
}

function parseCheckInt(arg) {
    const res = parseInt(arg);
    const floatRes = parseFloat(arg);
    if (isNaN(res) || !Number.isInteger(floatRes))
    {
        throw new Error("Expected integer parameter");
    }
    return res;
}

function parseCheckFloat(arg) {
    const res = parseFloat(arg);
    if (isNaN(res))
    {
        throw new Error("Expected number parameter");
    }
    return res;
}

function replacePlaceholder(arg) {
    return arg == "_" ? undefined : arg;
}

function parseOptionalInt(arg) {
    return replacePlaceholder(arg) != null ? parseCheckInt(replacePlaceholder(arg)) : undefined;
}

function parseOptionalFloat(arg) {
    return replacePlaceholder(arg) != null ? parseCheckFloat(replacePlaceholder(arg)) : undefined;
}

function buildName(op, args, len_i) {
    if (len_i > args.length-1)
    {
        return {name: undefined, currentLen: op.length};
    }

    let currentLen = 0;
    for (let i = 0; i < len_i; i++)
    {
        currentLen += args[i].length;
        while (op[currentLen] == " ")
        {
            currentLen++;
        }
    }

    if (args[len_i] == "_")
    {
        currentLen++;
        return {name: undefined, currentLen: currentLen + 1};
    }

    let stringLen = args[len_i].split(/:(.*)/)[0];
    currentLen += stringLen.length + 1;
    stringLen = parseCheckInt(stringLen);
    return {name: op.substring(currentLen, currentLen + stringLen), currentLen: currentLen + stringLen + 1};
}

function parseModelOp(op, args) {
    switch (args[0]) {
    case "LEVEL":
        BIM.createLevel(model, parseCheckInt(args[1]), parseCheckFloat(args[2]), buildName(op, args, 3).name);
        break;
    case "WALLTYPE":
        BIM.createWallType(model, args[1],
            parseOptionalFloat(args[2]),
            replacePlaceholder(args[3]),
            buildName(op, args, 4).name);
        break;
    case "WALL": {
        const wallId = args[1];
        const nPoints = parseCheckInt(args[2]);
        const path = [];
        for (let i = 0; i < nPoints; i++)
        {
            path.push({x: parseCheckFloat(args[3 + i * 2]), z: parseCheckFloat(args[4 + i * 2])});
        }
        const levelArg_i = 3 + nPoints * 2;
        BIM.createWall(model, wallId, path, parseCheckInt(args[levelArg_i]), {
            wallTypeId: replacePlaceholder(args[levelArg_i + 1]),
            topLevel: parseOptionalInt(args[levelArg_i + 2]),
            height: parseOptionalFloat(args[levelArg_i + 3]),
            copyUuid: replacePlaceholder(args[levelArg_i + 4]),
        });
        break;
    }
    case "SLABTYPE":
        BIM.createSlabType(model, args[1],
            parseOptionalFloat(args[2]),
            replacePlaceholder(args[3]),
            buildName(op, args, 4).name);
        break;
    case "SLAB": {
        const slabId = args[1];
        const nPoints = parseCheckInt(args[2]);
        const region = [];
        for (let i = 0; i < nPoints; i++)
        {
            region.push({x: parseCheckFloat(args[3 + i * 2]), z: parseCheckFloat(args[4 + i * 2])});
        }
        const levelArg_i = 3 + nPoints * 2;
        BIM.createSlab(model, slabId, region, parseCheckInt(args[levelArg_i]), {
            slabTypeId: replacePlaceholder(args[levelArg_i + 1])
        });
        break;
    }
    case "SLABRECT":
        BIM.createSlab(model, args[1], {
            start: {x: parseCheckFloat(args[2]), z: parseCheckFloat(args[3])},
            end: {x: parseCheckFloat(args[4]), z: parseCheckFloat(args[5])}
        }, parseCheckInt(args[6]), {
            slabTypeId: replacePlaceholder(args[7])
        });
        break;
    case "ROOF": {
        const roofId = args[1];
        const nPoints = parseCheckInt(args[2]);
        const region = [];
        for (let i = 0; i < nPoints; i++)
        {
            region.push({x: parseCheckFloat(args[3 + i * 2]), z: parseCheckFloat(args[4 + i * 2])});
        }
        const levelArg_i = 3 + nPoints * 2;
        BIM.createRoof(model, roofId, region, parseCheckInt(args[levelArg_i]), {
            roofTypeId: replacePlaceholder(args[levelArg_i + 1])
        });
        break;
    }
    case "BEAMTYPE": {
        const nPoints = parseOptionalInt(args[2]);
        let profile;
        let materialArg_i = 3;
        if (nPoints) {
            profile = [];
            for (let i = 0; i < nPoints; i++)
            {
                profile.push([parseCheckFloat(args[3 + i * 2]), parseCheckFloat(args[4 + i * 2])]);
            }
            materialArg_i = 3 + nPoints * 2;
        }
        BIM.createBeamType(model, args[1],
            profile,
            replacePlaceholder(args[materialArg_i]),
            buildName(op, args, materialArg_i + 1).name);
        break;
    }
    case "BEAM": {
        BIM.createBeam(model, [
            [parseCheckFloat(args[1]), parseCheckFloat(args[2])],
            [parseCheckFloat(args[3]), parseCheckFloat(args[4])],
        ], parseCheckInt(args[5]), {
            elevation: parseOptionalFloat(args[6]),
            beamTypeId: replacePlaceholder(args[7]),
        });
        break;
    }
    case "COLUMNTYPE": {
        const nPoints = parseOptionalInt(args[2]);
        let profile;
        let materialArg_i = 3;
        if (nPoints) {
            profile = [];
            for (let i = 0; i < nPoints; i++)
            {
                profile.push([parseCheckFloat(args[3 + i * 2]), parseCheckFloat(args[4 + i * 2])]);
            }
            materialArg_i = 3 + nPoints * 2;
        }
        BIM.createColumnType(model, args[1],
            profile,
            replacePlaceholder(args[materialArg_i]),
            buildName(op, args, materialArg_i + 1).name);
        break;
    }
    case "COLUMN": {
        BIM.createColumn(model, args[1], [
            parseCheckFloat(args[2]), parseCheckFloat(args[3]),
        ], parseCheckInt(args[4]), {
            columnTypeId: replacePlaceholder(args[5]),
            topPosition: replacePlaceholder(args[6]) ? [parseOptionalFloat(args[6]), parseOptionalFloat(args[7])] : undefined,
            angle: parseOptionalFloat(args[8]),
            topLevel: parseOptionalInt(args[9]),
            copyUuid: replacePlaceholder(args[10]),
        });
        break;
    }
    case "MATERIAL":
        let albedo = undefined;
        let albedoStr = replacePlaceholder(args[2]);
        if (albedoStr) {
            let albedoStrList = albedoStr.split(',');
            albedo = [
                parseCheckFloat(albedoStrList[0]),
                parseCheckFloat(albedoStrList[1]),
                parseCheckFloat(albedoStrList[2]),
            ];
        }

        const textureUrl = buildName(op, args, 6);
        const remainingString = op.substring(textureUrl.currentLen);
        const name = remainingString.length > 0
            ? buildName(remainingString, remainingString.split(' '), 0) : {name: undefined};

        BIM.createMaterial(model, args[1],
            albedo,
            parseOptionalFloat(args[3]),
            parseOptionalFloat(args[4]),
            parseOptionalFloat(args[5]),
            textureUrl.name,
            name.name,
        );
        break;
    case "OPENING":
        BIM.createOpening(model, args[1], parseCheckFloat(args[2]), parseCheckFloat(args[3]), parseCheckFloat(args[4]), parseCheckFloat(args[5]));
        break;
    case "OPENINGPOLY":
        const hostId = args[1];
        const nPoints = parseCheckInt(args[2]);
        const region = [];
        for (let i = 0; i < nPoints; i++)
        {
            region.push([parseCheckFloat(args[3 + i * 2]), parseCheckFloat(args[4 + i * 2])]);
        }
        BIM.createOpeningPoly(model, hostId, region);
        break;
    case "WINDOW": {
        const opening = BIM.createOpening(model, args[1], parseCheckFloat(args[2]), parseCheckFloat(args[3]), parseCheckFloat(args[4]), parseCheckFloat(args[5]));
        BIM.createWindow(model, args[1], opening);
        break;
    }
    case "DOOR": {
        const opening = BIM.createOpening(model, args[1], parseCheckFloat(args[2]), 0, parseCheckFloat(args[3]), parseCheckFloat(args[4]));
        BIM.createDoor(model, args[1], opening);
        break;
    }
    case "STAIRTYPE":
        BIM.createStairType(model, args[1],
            parseOptionalFloat(args[2]),
            parseOptionalFloat(args[3]),
            parseOptionalFloat(args[4]),
            replacePlaceholder(args[5]),
            buildName(op, args, 6).name,
        );
        break;
    case "STAIR":
        BIM.createStair(model, [
            parseCheckFloat(args[1]), parseCheckFloat(args[2]),
        ], [
            parseCheckFloat(args[3]), parseCheckFloat(args[4]),
        ], parseCheckInt(args[5]), {
            stairTypeId: replacePlaceholder(args[6]),
            topLevel: parseOptionalInt(args[7]),
        });
        break;
    default:
        break;
    }
}

function loadModel() {
    let oldModel = model;

    const startTime = performance.now();

    model = BIM.createModel();

    try {
        for (const op of modelOps) {
            parseModelOp(op.op, op.args);
        }
        BIM.finalizeModel(model);
    }
    catch (error) {
        console.log(error);
        BIM.destroyModel(model);
        model = oldModel;
        return;
    }

    const endTime = performance.now();
    console.log(`Generation time: ${endTime - startTime} ms`);

    if (oldModel) {
        treeView.removeModel(oldModel.id);
        BIM.destroyModel(oldModel);
    }
    treeView.addModel(model.id);

    renderModelLists(model);
}

let ws;
function startWebSocket() {
    ws = new WebSocket("ws://127.0.0.1:5001/");
    ws.onmessage = function(event) {
        if (document.getElementById("user_mode").value != "designer") {
            return;
        }

        parseOp(event.data);
    };
    ws.addEventListener("open", (e) => {
        showWSError(false);
    });
    ws.addEventListener("error", (e) => {
        showWSError(true);
    });
    ws.addEventListener("close", (e) => {
        showWSError(true);
    });
}
startWebSocket();

let fetchLock = false;

async function fetchModel() {
    if (document.getElementById("user_mode").value != "client" || fetchLock) {
        return;
    }

    fetchLock = true;

    modelOps.length = 0;

    const length = parseFloat(document.getElementById("width").value);
    const width = parseFloat(document.getElementById("floors").value);
    const clientModel = document.getElementById("client_model").value;
    let url;

    if (clientModel == "duplex")
    {
        const arg1 = parseFloat(document.getElementById("n_value").value);
        const arg2 = parseFloat(document.getElementById("length").value);
        url = `http://127.0.0.1:5000/duplex?floor0Height=${arg1}&floor1Height=${arg2}&length=${length}&width=${width}`;
    }
    else if (clientModel == "skyscraper")
    {
        const arg1 = parseFloat(document.getElementById("n_value").value);
        const arg2 = parseInt(document.getElementById("length").value);
        url = `http://127.0.0.1:5000/skyscraper?floorHeight=${arg1}&numberOfFloors=${arg2}&length=${length}&width=${width}`;
    }
    else if (clientModel == "cayan")
    {
        url = `http://127.0.0.1:5000/cayan`;
    }
    else if (clientModel == "isenberg")
    {
        url = `http://127.0.0.1:5000/isenberg`;
    }

    try {
        const startTime = performance.now();

        let blob = await fetch(url).then(response => {
            if (!response.ok) {
                return null;
            }
            return response.blob();
        });

        let text = await blob.text();
        text = text.split('\n');
        text.forEach(op => {
            parseOp(op);
        });

        console.log(`Total time: ${performance.now() - startTime} ms`);
    }
    catch (error) {
        console.log(error);
    }

    // It should already be in batch mode
    // loadModel();

    fetchLock = false;
}

//------------------------------------------------------------------------------------------------------------------
// --- UI Handlers ---
//------------------------------------------------------------------------------------------------------------------

function showWSError(doShow) {
    document.getElementById("connectionLabel").style.visibility = doShow ? "visible" : "hidden";
    document.getElementById("retryButton").style.visibility = doShow ? "visible" : "hidden";
}

document.getElementById("retryButton").addEventListener("click", () => {
    startWebSocket();
});

document.getElementById("n_value").addEventListener("input", () => {
    fetchModel();
});

document.getElementById("length").addEventListener("input", () => {
    fetchModel();
});

document.getElementById("width").addEventListener("input", () => {
    fetchModel();
});

document.getElementById("floors").addEventListener("input", () => {
    fetchModel();
});

document.getElementById("reloadButton").addEventListener("click", () => {
    fetchModel();
});

function showClientUI(doShow) {
    let visibilityString = doShow ? "visible" : "hidden";

    document.getElementById("n_value").style.visibility = visibilityString;
    document.getElementById("length").style.visibility = visibilityString;
    document.getElementById("width").style.visibility = visibilityString;
    document.getElementById("floors").style.visibility = visibilityString;

    document.getElementById("n_value_label").style.visibility = visibilityString;
    document.getElementById("length_label").style.visibility = visibilityString;
    document.getElementById("width_label").style.visibility = visibilityString;
    document.getElementById("floors_label").style.visibility = visibilityString;

    document.getElementById("client_model").style.visibility = visibilityString;
    document.getElementById("reloadButton").style.visibility = visibilityString;
}
showClientUI(false);

let previousUserMode = document.getElementById("user_mode").value;
document.getElementById("user_mode").addEventListener("input", () => {
    switch (document.getElementById("user_mode").value) {
    case "designer":
        batchMode = false;
        showClientUI(false);
        break;
    case "client":
        if (!confirm("Are you sure? The current model will be lost!")) {
            document.getElementById("user_mode").value = previousUserMode;
            break;
        }
        batchMode = true;
        showClientUI(true);
        fetchModel();
        break;
    default:
        break;
    }

    previousUserMode = document.getElementById("user_mode").value;
});

document.getElementById("client_model").addEventListener("input", () => {
    const arg1 = document.getElementById("n_value");
    const arg2 = document.getElementById("length");
    const arg3 = document.getElementById("width");
    const arg4 = document.getElementById("floors");

    switch (document.getElementById("client_model").value) {
    case "duplex":
        document.getElementById("n_value_label").innerHTML = "Ground Floor Height";
        document.getElementById("length_label").innerHTML = "1st Floor Height";
        arg1.min = 2.7; arg1.max = 6.7; arg1.value = 3.1; arg1.step = 0.2;
        arg2.min = 2.7; arg2.max = 6.7; arg2.value = 2.9; arg2.step = 0.2;
        arg3.min = 17.8; arg3.max = 30.8; arg3.value = 17.8; arg3.step = 1;
        arg4.min = 8.8; arg4.max = 30.8; arg4.value = 8.8; arg4.step = 1;
        fetchModel();
        break;
    case "skyscraper":
        document.getElementById("n_value_label").innerHTML = "Floor Height";
        document.getElementById("length_label").innerHTML = "Number of Floors";
        arg1.min = 2; arg1.max = 6; arg1.value = 4; arg1.step = 0.2;
        arg2.min = 1; arg2.max = 15; arg2.value = 10; arg2.step = 1;
        arg3.min = 10; arg3.max = 50; arg3.value = 30; arg3.step = 1;
        arg4.min = 10; arg4.max = 50; arg4.value = 20; arg4.step = 1;
        fetchModel();
        break;
    default:
        break;
    }
});

document.getElementById("gridButton").addEventListener("click", () => {
    const planesVisible = BIM.togglePlanesVisible();
    gridPlane.visible = planesVisible;
    originSphere.visible = planesVisible;
    for (const [_, mesh] of Object.entries(model.levelPlaneMeshes)) {
        mesh.visible = planesVisible;
    }
});

document.getElementById("cameraButton").addEventListener("click", () => {
    if (viewer.camera.projection == "ortho") {
        viewer.camera.projection = "perspective";
    }
    else {
        viewer.camera.projection = "ortho";
    }
});

document.getElementById("measureButton").addEventListener("click", () => {
    if (distanceMeasurementsMouseControl.active) {
        distanceMeasurementsMouseControl.deactivate();
    }
    else {
        distanceMeasurementsMouseControl.activate();
    }
});

// Sidebars

const treeBar = document.getElementById("treeViewWrapper");
const treeButton = document.getElementById("treeButton");

function showTreeBar(doShow) {
    treeBar.classList.toggle("closed", doShow != undefined ? !doShow : undefined);

    treeButton.textContent = treeBar.classList.contains("closed")
        ? "🌳"
        : "✕";
}

treeButton.addEventListener("click", () => {
    showTreeBar(undefined);
});

const propertiesBar = document.getElementById("propertiesBar");
const propertiesButton = document.getElementById("propertiesButton");

function showPropertiesBar(doShow) {
    propertiesBar.classList.toggle("closed", doShow != undefined ? !doShow : undefined);

    propertiesButton.textContent = propertiesBar.classList.contains("closed")
        ? "ℹ️"
        : "✕";
}

propertiesButton.addEventListener("click", () => {
    showPropertiesBar(undefined);
});

function addKeyValueLink(div, key, value) {
    div.innerHTML = `${key}: <span class="attribute-link">${value}</span>`;

    div.querySelector(".attribute-link").addEventListener("click", () => {
        const target = document.getElementById(value);

        if (target) {
            // Open the details element if applicable
            target.open = true;

            // Scroll it into view
            target.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

            // Optional: briefly highlight it
            target.classList.add("highlighted-node");
            setTimeout(() => {
                target.classList.remove("highlighted-node");
            }, 1500);
        }
    });
}

function inspectMetaObject(metaObject) {
    showPropertiesBar(true);
    document.getElementById("propertiesBar.none_selected").style.visibility = "hidden";
    document.getElementById("propertiesBar.name").innerHTML = `Name: ${metaObject.name}`;
    document.getElementById("propertiesBar.category").innerHTML = `Category: ${metaObject.type}`;

    const attributeListElement = document.getElementById("propertiesBar.attributeList");
    attributeListElement.innerHTML = "";
    Object.keys(metaObject.attributes).forEach(key => {
        const div = document.createElement("div");
        div.className = "text";
        const value = metaObject.attributes[key];
        if (typeof value === "object" && value.uuid) {
            addKeyValueLink(div, key, value.uuid);
        } else {
            div.textContent = `${key}: ${value}`;
        }
        attributeListElement.appendChild(div);
    });
}

function renderModelLists(model) {
    const lists = {
        "propertiesBar.materialList": model.materials,
        "propertiesBar.wallTypeList": model.wallTypes,
        "propertiesBar.slabTypeList": model.slabTypes,
        "propertiesBar.beamTypeList": model.beamTypes,
        "propertiesBar.columnTypeList": model.columnTypes,
        "propertiesBar.stairTypeList": model.stairTypes,
    }

    for (const elementName of Object.keys(lists)) {
        const listElement = document.getElementById(elementName);
        listElement.innerHTML = "";

        Object.keys(lists[elementName]).forEach(key => {
            const details = document.createElement("details");
            details.className = "text";
            details.id = key;
            if (lists[elementName][key].name) {
                details.innerHTML = `<summary>${lists[elementName][key].name} (${key})</summary>`;
            }
            else {
                details.innerHTML = `<summary>${key}</summary>`;
            }

            details.innerHTML += "<p></p>";
            Object.keys(lists[elementName][key].attributes).forEach(key2 => {
                const div = document.createElement("div");
                div.className = "text";
                const value = lists[elementName][key].attributes[key2];
                if (typeof value === "object" && value.uuid) {
                    addKeyValueLink(div, key2, value.uuid);
                } else {
                    div.textContent = `${key2}: ${value}`;
                }
                details.appendChild(div);
            });
            details.innerHTML += "<p></p>";

            listElement.appendChild(details);
        });
    }
}

// Performance stats
var stats = new Stats();
stats.dom.style.position = "fixed";
stats.dom.style.left = "0px";
stats.dom.style.bottom = "0px";
stats.dom.style.top = "auto"; // override default top position
document.body.appendChild(stats.dom);
function animate() {
	stats.update();
	requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
