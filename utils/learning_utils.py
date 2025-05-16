import logging
import json
from collections import defaultdict
from utils.model_utils import update_model_weights
from models import Feedback, ModelVersion, db
from config import Config

logger = logging.getLogger(__name__)

# Store feedback counts for tracking when to trigger learning
feedback_counts = defaultdict(int)

def process_feedback(feedback):
    """
    Process new feedback for continuous learning
    
    Args:
        feedback (Feedback): Feedback object
    """
    # Increment feedback count for this language
    feedback_counts[feedback.language] += 1
    
    # Check if we've reached the threshold to update the model
    if feedback_counts[feedback.language] >= Config.FEEDBACK_THRESHOLD:
        logger.info(f"Feedback threshold reached for {feedback.language}, triggering model update")
        
        # Get recent feedback for this language
        recent_feedback = Feedback.query.filter_by(
            language=feedback.language
        ).order_by(
            Feedback.created_at.desc()
        ).limit(100).all()
        
        # Prepare feedback data for model update
        feedback_data = []
        for fb in recent_feedback:
            # Only use feedback with corrected output
            if fb.corrected_output:
                feedback_data.append({
                    'input': fb.code_input,
                    'expected': fb.corrected_output or fb.model_output,
                    'feedback_type': fb.feedback_type
                })
        
        # Update model if we have valid feedback data
        if feedback_data:
            try:
                # Update model weights (simulated)
                update_result = update_model_weights(feedback_data)
                
                # Record model version update
                record_model_update(feedback.language, update_result, len(feedback_data))
                
                # Reset counter
                feedback_counts[feedback.language] = 0
                
            except Exception as e:
                logger.error(f"Error updating model for {feedback.language}: {str(e)}")
        else:
            logger.info(f"No valid feedback data for {feedback.language}, skipping update")

def record_completion_feedback(user_id, code_input, model_output, corrected_output, language, rating=None):
    """
    Record feedback for code completion
    
    Args:
        user_id (int): User ID
        code_input (str): Original code input
        model_output (str): Generated completion by model
        corrected_output (str): User corrected completion (optional)
        language (str): Programming language
        rating (int): User rating 1-5 (optional)
        
    Returns:
        Feedback: Created feedback object
    """
    try:
        feedback = Feedback(
            user_id=user_id,
            code_input=code_input,
            model_output=model_output,
            corrected_output=corrected_output,
            language=language,
            feedback_type='completion',
            rating=rating
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        # Process feedback for learning
        process_feedback(feedback)
        
        return feedback
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording completion feedback: {str(e)}")
        raise

def record_model_update(language, update_result, feedback_count):
    """
    Record a model update in the database
    
    Args:
        language (str): Programming language
        update_result (dict): Result from model update
        feedback_count (int): Number of feedback items used
    """
    try:
        # Create parameters JSON
        parameters = {
            "language": language,
            "feedback_count": feedback_count,
            "learning_rate": Config.LEARNING_RATE
        }
        
        # Create metrics JSON
        metrics = {
            "status": update_result.get("status", "unknown"),
            "message": update_result.get("message", "")
        }
        
        # Create new model version record
        model_version = ModelVersion(
            version=update_result.get("new_version", "0.1.0"),
            description=f"Updated model for {language} with {feedback_count} feedback items",
            parameters=json.dumps(parameters),
            performance_metrics=json.dumps(metrics)
        )
        
        db.session.add(model_version)
        db.session.commit()
        
        logger.info(f"Recorded model update: version {model_version.version}")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error recording model update: {str(e)}")
