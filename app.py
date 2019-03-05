from flask import Flask
import config

app = Flask('moop-tenant-service')
app.config.from_object(config)


def register_blueprint():
    from application.tenant import tenants
    app.register_blueprint(tenants, url_prefix='/service/v1')


register_blueprint()


@app.route('/')
def index():
    from auth import raise_status
    return raise_status(200)
