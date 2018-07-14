import os
import io
import json
import binascii
import numpy as np
import png
from flask import Flask, request
app = Flask(__name__)

CONFIG = None

def get_configuration():
    global CONFIG
    if CONFIG == None:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, 'config.json'), 'r') as f:
            t = f.read()
            CONFIG = json.loads(t)
    return CONFIG

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
    app._image = np.ones((200, 200), dtype=int)
    return 'new', 200

@app.route('/api/clear-rectangle', methods=['PUT'])
def put_api_clear_rectangle():
    x = int(request.args['x'])
    y = int(request.args['y'])
    width = int(request.args['width'])
    height = int(request.args['height'])

    print('clearing', x, y, width, height)
    app._image[x:x+width, y:y+height] = np.ones((width, height), dtype=int)
    return 'reset', 200

@app.route('/api/pixel', methods=['PUT'])
def put_api_pixel():
    x = int(request.form['x'])
    y = int(request.form['y'])
    #value = request.form['value']

    app._image[x, y] = 0
    return 'assigned', 200

@app.route('/api/rectangle-binary', methods=['GET'])
def get_rectangle_data():
    x = int(request.args['x'])
    y = int(request.args['y'])
    width = int(request.args['width'])
    height = int(request.args['height'])

    a = app._image

    f = io.BytesIO()      # binary mode is important
    for pix in a[x:x+width, y:y+height].reshape([-1]):
        if pix == 1:
            data = b'\xff\xff\xff\xff'
        else:
            data = b'\x00\x00\x00\xff'
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
<canvas id="myCanvas" width="{width}" height="{height}" style="border:1px solid #000000;">
</canvas>
<div id="info"></div>
<input type="checkbox" id="auto_update" name="auto_update" value="newsletter">
<label for="auto_update">Update image every 1 second.</label>
</body>
</html>""".format(width=w, height=h)

if __name__ == '__main__':
    put_api_blank_image()

    config = get_configuration()
    app.run(host=config.get('host', None), port=config['port'], threaded=True)
