# Web BIM viewer for AD

## Viewer

1. Install [Node.js](https://nodejs.org/).

2. Install packages:
```
cd viewer/
npm install
```

3. Start a development server:
```
npm run dev
```

Make sure to populate `viewer/textures/` with textures, for the examples that use them.

## Server

1. Install [Python](https://www.python.org/).

2. Install requirements:
```
cd server/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### HTTP server
```
python3 -m flask --app http_server.py run
```

### WebSocket server
```
python3

>>> import server
>>> server.start()
```

Try running some examples:
```
>>> import demo
>>> demo.build()

>>> import cayan
>>> server.batch()
>>> cayan.tower()
```

### Protocol tests

Run unit tests for the server-client communication protocol:
```
python3 protocol_test.py
```
