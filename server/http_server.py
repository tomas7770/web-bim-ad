import server
import duplex as duplexCode
import ifc.duplex as duplexIfc
import skyscraper as skyscraperCode
import ifc.skyscraper as skyscraperIfc
import cayan as cayanCode
import ifc.cayan as cayanIfc
import isenberg as isenbergCode
import ifc.isenberg as isenbergIfc

output_str = ""

def send(content):
    global output_str
    output_str += content + "\n"
server.send = send

def gen_duplex(floor0Height: float, floor1Height: float, length: float, width: float):
    global output_str
    output_str = ""
    duplexCode.duplex(floor0Height, floor1Height, length, width)

    return output_str

def gen_skyscraper(floorHeight: float, numberOfFloors: int, length: float, width: float):
    global output_str
    output_str = ""
    skyscraperCode.skyscraper(floorHeight, numberOfFloors, length, width)

    return output_str

def gen_cayan():
    global output_str
    output_str = ""
    cayanCode.tower()

    return output_str

def gen_isenberg():
    global output_str
    output_str = ""
    isenbergCode.isenberg()

    return output_str

def gen_duplex_ifc():
    return duplexIfc.gen_duplex_ifc()

def gen_skyscraper_ifc(floorHeight: float, numberOfFloors: int, length: float, width: float):
    return skyscraperIfc.gen_skyscraper_ifc(floorHeight, numberOfFloors, length, width)

def gen_cayan_tower_ifc():
    return cayanIfc.gen_cayan_tower_ifc()

def gen_isenberg_ifc():
    return isenbergIfc.gen_isenberg_ifc()

from flask import Flask, make_response, request, send_file
from flask_cors import CORS
from io import BytesIO

app = Flask(__name__)

CORS(app, origins=['http://localhost:5173', 'http://localhost:8000'])

@app.route("/duplex")
def duplex():
    floor0Height = request.args.get("floor0Height", 3.1, type = float)
    floor1Height = request.args.get("floor1Height", 2.9, type = float)
    length = request.args.get("length", 17.8, type = float)
    width = request.args.get("width", 8.8, type = float)

    model = gen_duplex(floor0Height, floor1Height, length, width)
    response = make_response(model, 200)
    response.mimetype = "text/plain"
    return response

@app.route("/skyscraper")
def skyscraper():
    floorHeight = request.args.get("floorHeight", 4, type = float)
    numberOfFloors = request.args.get("numberOfFloors", 10, type = int)
    length = request.args.get("length", 30, type = float)
    width = request.args.get("width", 20, type = float)

    model = gen_skyscraper(floorHeight, numberOfFloors, length, width)
    response = make_response(model, 200)
    response.mimetype = "text/plain"
    return response

@app.route("/cayan")
def cayan():
    model = gen_cayan()
    response = make_response(model, 200)
    response.mimetype = "text/plain"
    return response

@app.route("/isenberg")
def isenberg():
    model = gen_isenberg()
    response = make_response(model, 200)
    response.mimetype = "text/plain"
    return response

@app.route("/duplex_ifc")
def duplex_ifc():
    model = gen_duplex_ifc()
    return send_file(BytesIO(bytes(model, "utf-8")), "application/p21")

@app.route("/skyscraper_ifc")
def skyscraper_ifc():
    floorHeight = request.args.get("floorHeight", 4, type = float)
    numberOfFloors = request.args.get("numberOfFloors", 10, type = int)
    length = request.args.get("length", 30, type = float)
    width = request.args.get("width", 20, type = float)

    model = gen_skyscraper_ifc(floorHeight, numberOfFloors, length, width)
    return send_file(BytesIO(bytes(model, "utf-8")), "application/p21")

@app.route("/cayan_tower_ifc")
def cayan_tower_ifc():
    model = gen_cayan_tower_ifc()
    return send_file(BytesIO(bytes(model, "utf-8")), "application/p21")

@app.route("/isenberg_ifc")
def isenberg_ifc():
    model = gen_isenberg_ifc()
    return send_file(BytesIO(bytes(model, "utf-8")), "application/p21")
