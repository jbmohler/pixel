import os
import io
import json
import math
import binascii
import threading
import numpy as np
import png
from flask import Flask, request
app = Flask(__name__)

CONFIG = None
SIDE_LENGTH = 800

UPDATE_HISTORY = []
UPDATE_BASE_INDEX = 0
UPDATE_EVENT = threading.Event()

def add_change_node(x1, y1, x2, y2):
    global UPDATE_HISTORY, UPDATE_EVENT
    UPDATE_HISTORY.append((x1, y1, x2, y2))
    UPDATE_EVENT.set()

def change_rect_since(histindex):
    global UPDATE_HISTORY, UPDATE_BASE_INDEX

    rect = [None, None, None, None]
    for node in UPDATE_HISTORY[histindex-UPDATE_BASE_INDEX:]:
        if rect[0] == None or rect[0] > node[0]:
            rect[0] = node[0]
        if rect[1] == None or rect[1] > node[1]:
            rect[1] = node[1]
        if rect[2] == None or rect[2] < node[2]:
            rect[2] = node[2]
        if rect[3] == None or rect[3] < node[3]:
            rect[3] = node[3]
    return rect

def get_configuration():
    global CONFIG
    if CONFIG == None:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, 'config.json'), 'r') as f:
            t = f.read()
            CONFIG = json.loads(t)
    return CONFIG

def parse_color(color):
    if color == True:
        return 0
    elif color == False:
        return 0xffffff
    color = color.lower()
    if len(color) == 7 and color[0] == '#' and set(color[1:]).issubset('0123456789abcdef'):
        return int(color[1:], 16)
    raise RuntimeError('unrecognized color -- {}'.format(color))

@app.route('/')
def hello():
    config = get_configuration()
    return 'Hello World -- {}!'.format(config['name'])

@app.route('/api/long')
def api_long():
    import time
    time.sleep(15)
    config = get_configuration()
    return 'Hello World -- {}!'.format(config['name'])

@app.route('/api/blank-image', methods=['PUT'])
def put_api_blank_image():
    app._image = np.ones((SIDE_LENGTH, SIDE_LENGTH), dtype=int)*0xffffff
    add_change_node(0, 0, SIDE_LENGTH-1, SIDE_LENGTH-1)
    return 'new', 200

@app.route('/api/clear-rectangle', methods=['PUT'])
def put_api_clear_rectangle():
    x = int(request.form['x'])
    y = int(request.form['y'])
    width = int(request.form['width'])
    height = int(request.form['height'])

    app._image[x:x+width, y:y+height] = np.ones((width, height), dtype=int)*0xffffff
    add_change_node(x, y, x+width, y+height)
    return 'reset', 200

@app.route('/api/ellipse', methods=['PUT'])
def put_api_ellipse():
    xcenter = int(request.form['xcenter'])
    ycenter = int(request.form['ycenter'])
    xradius = int(request.form['xradius'])
    yradius = int(request.form['yradius'])
    color = request.form.get('color', '#000000')
    color = parse_color(color)

    xradius = abs(xradius)
    yradius = abs(yradius)

    pntcount = 6*(xradius + yradius)

    for i in range(pntcount):
        angle = float(i)/pntcount * 2*math.pi

        x = xcenter + xradius*math.sin(angle)
        y = ycenter + yradius*math.cos(angle)

        x = int(x+.5) # round to nearest
        y = int(y+.5) # round to nearest
        app._image[x, y] = color

    add_change_node(xcenter-xradius-1, ycenter-yradius-1, xcenter+xradius+1, ycenter+yradius+1)
    return 'assigned', 200

@app.route('/api/line', methods=['PUT'])
def put_api_line():
    x1 = int(request.form['x1'])
    y1 = int(request.form['y1'])
    x2 = int(request.form['x2'])
    y2 = int(request.form['y2'])
    color = request.form.get('color', '#000000')
    color = parse_color(color)

    xa, xb = sorted([x1, x2])
    ya, yb = sorted([y1, y2])

    # remember y=mx+b
    if x1 == x2:
        # horizontal
        for y in range(ya, yb+1):
            app._image[x1, y] = color
    elif y1 == y2:
        # horizontal
        for x in range(xa, xb+1):
            app._image[x1, y] = color
    elif xb - xa < yb - ya:
        # y axis as independent
        m = float(x2-x1)/float(y2-y1)
        b = float(x1)-m*float(y1)
        if y2 >= y1:
            rr = range(y1, y2+1)
        else:
            rr = range(y1, y2-1, -1)
        for y in rr:
            x = m*y+b
            x = int(x+.5) # round to nearest
            app._image[x, y] = color
    else:
        # x axis as independent
        m = float(y2-y1)/float(x2-x1)
        b = float(y1)-m*float(x1)
        if x2 >= x1:
            rr = range(x1, x2+1)
        else:
            rr = range(x1, x2-1, -1)
        for x in rr:
            y = m*x+b
            y = int(y+.5) # round to nearest
            app._image[x, y] = color
    add_change_node(xa, ya, xb, yb)
    return 'assigned', 200

@app.route('/api/pixel', methods=['PUT'])
def put_api_pixel():
    x = int(request.form['x'])
    y = int(request.form['y'])
    color = request.form.get('color', '#000000')
    color = parse_color(color)

    app._image[x, y] = color
    add_change_node(x, y, x, y)
    return 'assigned', 200

@app.route('/api/change-poll', methods=['GET'])
def get_api_change_poll():
    global UPDATE_EVENT, UPDATE_HISTORY
    last = int(request.args['last'])

    histnow = len(UPDATE_HISTORY)

    if histnow <= last:
        UPDATE_EVENT.clear()

        UPDATE_EVENT.wait(90)

    histx = len(UPDATE_HISTORY)
    
    x1, y1, x2, y2 = change_rect_since(last)

    if x1 != None:
        a = app._image

        f = io.BytesIO()      # binary mode is important
        for pix in a[x1:x2+1, y1:y2+1].reshape([-1], order='F'):
            b1, b2, b3 = (pix // 256**2 % 256), (pix // 256) % 256, pix % 256
            data = bytearray([b1, b2, b3, 255])
            f.write(data)
        imdata = binascii.hexlify(f.getvalue()).decode('ascii')
        f.close()

        content = {
                'x': x1,
                'y': y1,
                'width': x2-x1+1,
                'height': y2-y1+1,
                'imdata': imdata,
                'histnode': histx}
    else:
        content = {}

    headers = {'Content-Type': 'application/json'}
    return json.dumps(content), 200, headers

@app.route('/api/rectangle-binary', methods=['GET'])
def get_rectangle_data():
    global UPDATE_HISTORY
    x = int(request.args['x'])
    y = int(request.args['y'])
    width = int(request.args['width'])
    height = int(request.args['height'])

    a = app._image

    f = io.BytesIO()      # binary mode is important
    for pix in a[x:x+width, y:y+height].reshape([-1], order='F'):
        b1, b2, b3 = (pix // 256**2 % 256), (pix // 256) % 256, pix % 256
        data = bytearray([b1, b2, b3, 255])
        f.write(data)
    imdata = binascii.hexlify(f.getvalue()).decode('ascii')
    f.close()
    content = {
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'imdata': imdata}

    headers = {'Content-Type': 'application/json'}
    return json.dumps(content), 200, headers

@app.route('/pixel-image.png')
def get_pixel_image():
    a = app._image

    f = io.BytesIO()      # binary mode is important
    w = png.Writer(a.shape[0], a.shape[1], greyscale=True, bitdepth=1)
    w.write(f, a)
    content = f.getvalue()
    f.close()

    headers = {'Content-Type': 'image/png'}
    return content, 200, headers

@app.route('/client.js')
def get_static_file():
    headers = {'Content-Type': 'application/javascript'}
    return open('server/client.js', 'r').read(), 200, headers

@app.route('/current.html')
def get_current_html():
    w, h = app._image.shape

    return """
<html>
<head>
	<title>Canvas Fun</title>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
        <script src="client.js"></script>
</head>
<body>
    <div id="dcan" style="float: left">
        <canvas id="myCanvas" width="{width}" height="{height}" style="border:1px solid #000000;">
        </canvas>
        <div id="info"></div>
        <!-- <input type="checkbox" id="auto_update" name="auto_update" value="newsletter">
        <label for="auto_update">Update image every 1 second.</label> -->
    </div>
</body>
</html>""".format(width=w, height=h)

if __name__ == '__main__':
    put_api_blank_image()

    config = get_configuration()
    app.run(host=config.get('host', None), port=config['port'], threaded=True)
