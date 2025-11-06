from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_app(config_class='config.Config'):
    
    app = Flask(__name__)

    app.config.from_object(config_class)

    CORS(app)

    with app.app_context():
        
        from . import routes
        app.register_blueprint(routes.main_bp)

    return app