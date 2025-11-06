from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
load_dotenv()

def create_app(config_class='config.Config'):
    
    app = Flask(__name__)

    app.config.from_object(config_class)

    frontend_url = os.getenv("FRONTEND_URL")
    print(frontend_url)

    CORS(app, 
         origins=[frontend_url] 
    )

    with app.app_context():
        
        from . import routes
        app.register_blueprint(routes.main_bp)

    return app