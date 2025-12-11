from flask import Flask
from .main import register_routes


def create_app() -> Flask:
    """
    Application factory for the Admissions Eligibility Checker API.
    """
    app = Flask(__name__)
    register_routes(app)
    return app
