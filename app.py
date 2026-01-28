from flask import Flask
from config import Config
from routes.auth_routes import auth_routes
from routes.dashboard_routes import dashboard_routes
from routes.application_routes import application_routes

from routes.profile_routes import profile_routes


def create_app():
    app = Flask(__name__, template_folder="views")  # <--- specify template folder
    app.config.from_object(Config)

    app.register_blueprint(auth_routes)
    app.register_blueprint(dashboard_routes)
    app.register_blueprint(profile_routes)
    app.register_blueprint(application_routes)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
