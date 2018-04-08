import os
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

@app.route('/api/pixel', methods=['PUT'])
def put_api_pixel():
    x = int(request.form['x'])
    y = int(request.form['y'])
    value = request.form['value']

    print(x, y, value)
    app._image = np.zeros((10, 10), dtype=int)
    app._image[x, y] = 1
    print(app._image)
    return 'assigned', 200

@app.route('/pixel-image.png')
def get_pixel_image():
    import io
    pig = io.BytesIO()
    im = Image.fromarray(app._image)
    im.save(pig, 'png')
    return pig.data(), 200

if __name__ == '__main__':
    config = get_configuration()
    app.run(port=config['port'])
