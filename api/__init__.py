from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import all API routes
from api.code_completion import *
from api.error_checking import *
from api.language_detection import *
from api.feedback import *
from api.ai_thinking import *
from api.try_api import *
from api.web_learning import *
