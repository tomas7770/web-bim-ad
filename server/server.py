from websockets.sync.server import serve
import threading
import uuid as uuidGen
import protocol

last_id = 0
clients = dict()

def handler(websocket):
    global last_id
    global current_id
    id = last_id
    last_id += 1
    clients[id] = websocket
    if auto_select_last:
        current_id = id
    try:
        websocket.recv()
    except:
        del clients[id]

def main():
    server = serve(handler, "localhost", 5001)
    print("Server is running on ws://localhost:5001")
    server.serve_forever()

def start():
    threading.Thread(target=main).start()

current_id = 0
auto_select_last = True

def getClient():
    return clients.get(current_id)

def send(content):
    getClient().send(content)

def batch():
    send("BATCH")

def interactive():
    send("INTERACTIVE")

def finish():
    send("FINISH")

def clear():
    send("CLEAR")

def clearBatch():
    clear()
    finish()

def undo():
    send("UNDO")

def createLevel(i, elevation, name = None):
    send(protocol.level(i, elevation, name))

def createWallType(thickness = None, material = None, name = None):
    uuid = uuidGen.uuid1()
    send(protocol.wallType(uuid, thickness, material, name))
    return uuid

def createWall(path, bottomLevel, wallType = None, topLevel = None, height = None, copyUuid = None):
    uuid = uuidGen.uuid1()
    send(protocol.wall(uuid, path, bottomLevel, wallType, topLevel, height, copyUuid))
    return uuid

def createSlabType(thickness = None, material = None, name = None):
    uuid = uuidGen.uuid1()
    send(protocol.slabType(uuid, thickness, material, name))
    return uuid

def createSlab(region, level, slabType = None):
    uuid = uuidGen.uuid1()
    if isinstance(region, dict):
        send(protocol.slabRect(uuid, region, level, slabType))
    else:
        send(protocol.slab(uuid, region, level, slabType))
    return uuid

def createRoofType(thickness = None, material = None, name = "Roof"):
    # This is the same as a slab type under the hood
    uuid = uuidGen.uuid1()
    send(protocol.slabType(uuid, thickness, material, name))
    return uuid

def createRoof(region, level, roofType = None):
    uuid = uuidGen.uuid1()
    send(protocol.roof(uuid, region, level, roofType))
    return uuid

def createBeamType(profile = None, material = None, name = None):
    uuid = uuidGen.uuid1()
    send(protocol.beamType(uuid, profile, material, name))
    return uuid

def createBeam(line, level, elevation = None, beamType = None):
    send(protocol.beam(line, level, elevation, beamType))

def createColumnType(profile = None, material = None, name = None):
    uuid = uuidGen.uuid1()
    send(protocol.columnType(uuid, profile, material, name))
    return uuid

def createColumn(position, bottomLevel, columnType = None, topPosition = None, angle = None, topLevel = None, copyUuid = None):
    uuid = uuidGen.uuid1()
    send(protocol.column(uuid, position, bottomLevel, columnType, topPosition, angle, topLevel, copyUuid))
    return uuid

def createMaterial(albedo = None, opacity = None, xScale = None, yScale = None, texturePath = None, name = None):
    uuid = uuidGen.uuid1()
    send(protocol.material(uuid, albedo, opacity, xScale, yScale, texturePath, name))
    return uuid

def createOpening(host, posX, posY, sizeX, sizeY):
    send(protocol.opening(host, posX, posY, sizeX, sizeY))

def createOpeningPoly(host, region):
    send(protocol.openingPoly(host, region))

def createWindow(host, posX, posY, sizeX, sizeY):
    send(protocol.window(host, posX, posY, sizeX, sizeY))

def createDoor(host, posX, sizeX, sizeY):
    send(protocol.door(host, posX, sizeX, sizeY))

def createStairType(width = None, height = None, depth = None, material = None, name = None):
    uuid = uuidGen.uuid1()
    send(protocol.stairType(uuid, width, height, depth, material, name))
    return uuid

def createStair(basePoint, direction, bottomLevel, stairType = None, topLevel = None):
    send(protocol.stair(basePoint, direction, bottomLevel, stairType, topLevel))
