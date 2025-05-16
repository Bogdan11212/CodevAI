import threading
import time
import logging
from app import app
from brain.continuous_learning import start_continuous_learning

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Initialize continuous learning system
    start_continuous_learning()
    
    # Start web server
    app.run(host="0.0.0.0", port=5000, debug=True)
