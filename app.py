import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy with the Base class
db = SQLAlchemy(model_class=Base)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database - используем локальную SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///codevai.db'
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Отключаем некоторые предупреждения SQLAlchemy
app.config["SQLALCHEMY_WARN_20"] = False

# Initialize the database with the app
db.init_app(app)

# Import models to ensure tables are created
with app.app_context():
    import models
    db.create_all()

    # Import and register API blueprints
    from api import api_bp
    from api.cloudflare_routes import cloudflare_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(cloudflare_bp)
    
    # Import routes
    from routes import *
    
    # Initialize continuous learning on application startup
    from brain.continuous_learning import start_continuous_learning
    start_continuous_learning()

    logger.info("Application initialized successfully")
