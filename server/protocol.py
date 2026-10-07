from uuid import UUID

def level(i, elevation, name = None):
    assert(isinstance(i, int))
    assert(isinstance(elevation, (int, float)))
    assert(isinstance(name, str) if name else True)

    return f"LEVEL {i} {elevation}" + optionalArgs(string(name))

def optionalArgs(*args):
    out = ""

    lastDefinedArg = -1
    for i in range(len(args)):
        if args[i] != None:
            lastDefinedArg = i

    for i in range(lastDefinedArg + 1):
        if args[i] != None:
            out += f" {args[i]}"
        else:
            out += " _"

    return out

def string(text):
    if text == None:
        return None
    assert(isinstance(text, str))
    text = text.replace("\n", " ")
    return f"{len(text)}:{text}"

def wallType(uuid, thickness = None, material = None, name = None):
    assert(isinstance(uuid, UUID))
    assert(isinstance(thickness, (int, float)) if thickness else True)
    assert(isinstance(material, UUID) if material else True)
    assert(isinstance(name, str) if name else True)

    # Note: name must currently be the last argument because it's a string which may contain spaces,
    # and there are no delimiters
    out = f"WALLTYPE {uuid}" + optionalArgs(thickness, material, string(name))

    return out

def wall(uuid, path, bottomLevel, wallType = None, topLevel = None, height = None, copyUuid = None):
    assert(isinstance(uuid, UUID))
    assert(isinstance(path, (list, tuple)))
    assert(isinstance(bottomLevel, int))
    assert(isinstance(wallType, UUID) if wallType else True)
    assert(isinstance(topLevel, int) if topLevel else True)
    assert(isinstance(height, (int, float)) if height else True)
    assert(isinstance(copyUuid, UUID) if copyUuid else True)

    assert(len(path) >= 2)

    out = f"WALL {uuid} {len(path)}"
    for point in path:
        out += f" {point[0]} {point[1]}"
    out += f" {bottomLevel}" + optionalArgs(wallType, topLevel, height, copyUuid)

    return out

def slabType(uuid, thickness = None, material = None, name = None):
    assert(isinstance(uuid, UUID))
    assert(isinstance(thickness, (int, float)) if thickness else True)
    assert(isinstance(material, UUID) if material else True)
    assert(isinstance(name, str) if name else True)

    out = f"SLABTYPE {uuid}" + optionalArgs(thickness, material, string(name))

    return out

def slab(uuid, region, level, slabType = None):
    assert(isinstance(uuid, UUID))
    assert(isinstance(region, (list, tuple)))
    assert(isinstance(level, int))
    assert(isinstance(slabType, UUID) if slabType else True)

    assert(len(region) >= 3)

    out = f"SLAB {uuid} {len(region)}"
    for point in region:
        out += f" {point[0]} {point[1]}"
    out += f" {level}"

    if slabType == None:
        return out
    out += f" {slabType}"

    return out

def slabRect(uuid, rect, level, slabType = None):
    assert(isinstance(uuid, UUID))
    assert(isinstance(rect, dict))
    assert(isinstance(level, int))
    assert(isinstance(slabType, UUID) if slabType else True)

    out = f"SLABRECT {uuid} {rect["start"][0]} {rect["start"][1]} {rect["end"][0]} {rect["end"][1]} {level}"
    if slabType == None:
        return out
    out += f" {slabType}"
    return out

def roof(uuid, region, level, roofType = None):
    assert(isinstance(uuid, UUID))
    assert(isinstance(region, (list, tuple)))
    assert(isinstance(level, int))
    assert(isinstance(roofType, UUID) if roofType else True)

    assert(len(region) >= 3)
    out = f"ROOF {uuid} {len(region)}"
    for point in region:
        out += f" {point[0]} {point[1]}"
    out += f" {level}"

    if roofType == None:
        return out
    out += f" {roofType}"

    return out

def beamType(uuid, profile = None, material = None, name = None):
    assert(isinstance(uuid, UUID))
    assert(isinstance(profile, (list, tuple)) if profile else True)
    assert(isinstance(material, UUID) if material else True)
    assert(isinstance(name, str) if name else True)

    out = f"BEAMTYPE {uuid}"
    if profile:
        assert(len(profile) >= 3)
        out += f" {len(profile)}"
        for point in profile:
            out += f" {point[0]} {point[1]}"

        out += optionalArgs(material, string(name))
    else:
        out += optionalArgs(None, material, string(name))

    return out

def beam(line, level, elevation = None, beamType = None):
    assert(isinstance(line, (list, tuple)))
    assert(isinstance(level, int))
    assert(isinstance(elevation, (int, float)) if elevation else True)
    assert(isinstance(beamType, UUID) if beamType else True)

    assert(len(line) == 2)

    out = f"BEAM {line[0][0]} {line[0][1]} {line[1][0]} {line[1][1]} {level}" + optionalArgs(elevation, beamType)

    return out

def columnType(uuid, profile = None, material = None, name = None):
    assert(isinstance(uuid, UUID))
    assert(isinstance(profile, (list, tuple)) if profile else True)
    assert(isinstance(material, UUID) if material else True)
    assert(isinstance(name, str) if name else True)

    out = f"COLUMNTYPE {uuid}"
    if profile:
        assert(len(profile) >= 3)
        out += f" {len(profile)}"
        for point in profile:
            out += f" {point[0]} {point[1]}"

        out += optionalArgs(material, string(name))
    else:
        out += optionalArgs(None, material, string(name))

    return out

def column(uuid, position, bottomLevel, columnType = None, topPosition = None, angle = None, topLevel = None, copyUuid = None):
    assert(isinstance(uuid, UUID))
    assert(isinstance(bottomLevel, int))
    assert(isinstance(columnType, UUID) if columnType else True)
    assert(isinstance(angle, (int, float)) if angle else True)
    assert(isinstance(topLevel, int) if topLevel else True)
    assert(isinstance(copyUuid, UUID) if copyUuid else True)

    out = f"COLUMN {uuid} {position[0]} {position[1]} {bottomLevel}" + \
        optionalArgs(columnType, topPosition[0] if topPosition else None, topPosition[1] if topPosition else None,
                     angle, topLevel, copyUuid)

    return out

def material(uuid, albedo = None, opacity = None, xScale = None, yScale = None, texturePath = None, name = None):
    assert(isinstance(uuid, UUID))
    assert(isinstance(opacity, (int, float)) if opacity else True)
    assert(isinstance(xScale, (int, float)) if xScale else True)
    assert(isinstance(yScale, (int, float)) if yScale else True)
    assert(isinstance(texturePath, str) if texturePath else True)
    assert(isinstance(name, str) if name else True)

    if albedo:
        assert(len(albedo) == 3)
        albedoStr = f"{albedo[0]},{albedo[1]},{albedo[2]}"
    out = f"MATERIAL {uuid}" + optionalArgs(albedoStr if albedo else None, opacity, xScale, yScale, string(texturePath), string(name))

    return out

def opening(host_uuid, posX, posY, sizeX, sizeY):
    assert(isinstance(host_uuid, UUID))
    assert(isinstance(posX, (int, float)))
    assert(isinstance(posY, (int, float)))
    assert(isinstance(sizeX, (int, float)))
    assert(isinstance(sizeY, (int, float)))

    return f"OPENING {host_uuid} {posX} {posY} {sizeX} {sizeY}"

def openingPoly(host_uuid, region):
    assert(isinstance(host_uuid, UUID))
    assert(isinstance(region, (list, tuple)))

    assert(len(region) >= 3)

    out = f"OPENINGPOLY {host_uuid} {len(region)}"
    for point in region:
        out += f" {point[0]} {point[1]}"

    return out

def window(host_uuid, posX, posY, sizeX, sizeY):
    assert(isinstance(host_uuid, UUID))
    assert(isinstance(posX, (int, float)))
    assert(isinstance(posY, (int, float)))
    assert(isinstance(sizeX, (int, float)))
    assert(isinstance(sizeY, (int, float)))

    return f"WINDOW {host_uuid} {posX} {posY} {sizeX} {sizeY}"

def door(host_uuid, posX, sizeX, sizeY):
    assert(isinstance(host_uuid, UUID))
    assert(isinstance(posX, (int, float)))
    assert(isinstance(sizeX, (int, float)))
    assert(isinstance(sizeY, (int, float)))

    return f"DOOR {host_uuid} {posX} {sizeX} {sizeY}"

def stairType(uuid, width = None, height = None, depth = None, material = None, name = None):
    assert(isinstance(uuid, UUID))
    assert(isinstance(width, (int, float)) if width else True)
    assert(isinstance(height, (int, float)) if height else True)
    assert(isinstance(depth, (int, float)) if depth else True)
    assert(isinstance(material, UUID) if material else True)
    assert(isinstance(name, str) if name else True)

    return f"STAIRTYPE {uuid}" + optionalArgs(width, height, depth, material, string(name))

def stair(basePoint, direction, bottomLevel, stairType = None, topLevel = None):
    assert(isinstance(bottomLevel, int))
    assert(isinstance(stairType, UUID) if stairType else True)
    assert(isinstance(topLevel, int) if topLevel else True)

    return f"STAIR {basePoint[0]} {basePoint[1]} {direction[0]} {direction[1]} {bottomLevel}" + optionalArgs(stairType, topLevel)
