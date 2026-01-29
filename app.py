from flask import Flask, app
from flask_cors import CORS
from config import Config
from routes.auth_routes import auth_routes
from routes.dashboard_routes import dashboard_routes
from routes.application_routes import application_routes

from routes.profile_routes import profile_routes

from routes.section_preferences_routes import section_preferences_routes


def create_app():
    app = Flask(__name__, template_folder="views")  # <--- specify template folder
    CORS(app)  # allow all origins (dev only!)
    app.config.from_object(Config)

    @app.route("/")
    def index():
        return "Flask app is running 🚀 here"

    app.register_blueprint(auth_routes)
    app.register_blueprint(dashboard_routes)
    app.register_blueprint(profile_routes)
    app.register_blueprint(application_routes)

    app.register_blueprint(section_preferences_routes)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
