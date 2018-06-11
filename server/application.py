import os
import io
import json
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
    app._image = np.ones((100, 100), dtype=int)
    return 'new', 200

@app.route('/api/pixel', methods=['PUT'])
def put_api_pixel():
    x = int(request.form['x'])
    y = int(request.form['y'])
    #value = request.form['value']

    app._image[x, y] = 0
    return 'assigned', 200

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

@app.route('/current.html')
def get_current_html():
    return """
<html>
 <head>
  <meta http-equiv="refresh" content="3">
 </head>
 <body>
 <img src='/pixel-image.png' alt='the current image' />
 </body>
</html>"""

if __name__ == '__main__':
    put_api_blank_image()

    config = get_configuration()
    app.run(port=config['port'])
