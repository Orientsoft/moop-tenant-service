from flask import Flask
from copy import deepcopy
import yaml


def import_config():
    with open('config.yaml', 'r', encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    config = data['config']
    cfg = deepcopy(config)
    return cfg


app = Flask('moop-tenant-service')
config = import_config()
for cfg in config:
    app.config[cfg] = config[cfg]


def register_blueprint():
    from application.tenant import tenants
    app.register_blueprint(tenants)


register_blueprint()


@app.route('/')
def index():
    from auth import raise_status
    return raise_status(200)
