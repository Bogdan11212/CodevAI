from app import db
from datetime import datetime

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code_input = db.Column(db.Text, nullable=False)
    model_output = db.Column(db.Text, nullable=False)
    corrected_output = db.Column(db.Text)
    language = db.Column(db.String(50), nullable=False)
    feedback_type = db.Column(db.String(50), nullable=False)  # 'completion', 'error', 'suggestion', 'generation'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer)  # 1-5 star rating
    
    def __repr__(self):
        return f'<Feedback {self.id} - {self.feedback_type}>'

class CodeExample(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(50), nullable=False)
    code_snippet = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)
    category = db.Column(db.String(100))  # e.g., 'syntax', 'algorithm', 'pattern'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CodeExample {self.id} - {self.language} - {self.category}>'
    
class ModelVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    parameters = db.Column(db.Text)  # JSON string of model parameters
    performance_metrics = db.Column(db.Text)  # JSON string of metrics
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ModelVersion {self.version}>'
