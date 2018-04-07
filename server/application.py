import os
import json
from flask import Flask
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

@app.route("/")
def hello():
    config = get_configuration()
    return "Hello World -- {}!".format(config['name'])

if __name__ == "__main__":
    config = get_configuration()
    app.run(port=config['port'])
