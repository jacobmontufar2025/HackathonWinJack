from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import sys

# Import your existing analyzer functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import, but create fallbacks if not available
try:
    from github_analyzer import (
        get_user_profile, 
        get_top_repos, 
        scan_repo_content, 
        analyze_candidate
    )
except ImportError:
    # Fallback mock functions for testing
    def get_user_profile(username):
        return {
            "username": username,
            "name": username.title(),
            "bio": "Mock bio for testing",
            "public_repos": 24,
            "followers": 128
        }
    
    def analyze_candidate(profile, repos_context):
        return {
            "candidate_name": profile.get('name'),
            "technical_score": 85,
            "estimated_level": "Senior",
            "primary_languages": ["Python", "JavaScript"],
            "technical_strengths": ["Clean code", "Good documentation"],
            "red_flags": ["None"],
            "hiring_verdict": "Strong Hire",
            "summary_report": "Excellent candidate with strong technical skills."
        }

app = Flask(__name__)
# Allow requests from your frontend
CORS(app, resources={r"/*": {"origins": "*"}})  # In production, specify your frontend URL

@app.route('/api/analyze-profile', methods=['POST'])
def analyze_profile():
    """Get GitHub profile data"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({"error": "Username is required"}), 400
        
        profile = get_user_profile(username)
        
        if not profile:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify(profile)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate full technical report"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({"error": "Username is required"}), 400
        
        # Get profile
        profile = get_user_profile(username)
        if not profile:
            return jsonify({"error": "User not found"}), 404
        
        # Get top repos
        top_repos = get_top_repos(username, limit=3)
        
        if not top_repos:
            return jsonify({"error": "No repositories found"}), 404
        
        # Scan each repo
        full_context = ""
        for repo in top_repos:
            repo_context = scan_repo_content(username, repo['name'])
            full_context += repo_context
        
        # Generate analysis
        report = analyze_candidate(profile, full_context)
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "GitHub Analyzer API"})

if __name__ == '__main__':
    # Run on all interfaces (0.0.0.0) for external access
    app.run(host='0.0.0.0', port=5000, debug=True)