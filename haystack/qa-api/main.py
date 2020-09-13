import connexion
from flask_cors import CORS
from app.qa import get_finder


def create_app():
    app = connexion.App('qa-app', specification_dir='swagger/')
    CORS(app.app)
    app.add_api('rest-api.yaml')
    app.app.config.from_object('app.default_settings')

    return app


app = create_app()


@app.app.before_first_request
def create_finder():
    get_finder()


if __name__ == '__main__':
    create_app().run(port=8080)
