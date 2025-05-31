from app import db
from datetime import datetime

class Comparison(db.Model):
    """Store comparison results for potential caching/analytics"""
    id = db.Column(db.Integer, primary_key=True)
    article_title = db.Column(db.String(500), nullable=False)
    languages = db.Column(db.Text, nullable=False)  # JSON string
    output_language = db.Column(db.String(10), nullable=False)
    mode = db.Column(db.String(20), nullable=False)
    result_hash = db.Column(db.String(64), nullable=False)  # For caching
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Comparison {self.article_title}>'

class SearchQuery(db.Model):
    """Track search queries for analytics"""
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(500), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    results_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SearchQuery {self.query}>'
