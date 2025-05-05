from flask import Flask, request, jsonify
import sys
import os
from flask_cors import CORS
import json
import sqlite3

# Add the model directory to the path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'model'))
from main import JobScreeningSystem, JDSummarizerAgent, CVParsingAgent, CandidateMatcherAgent, InterviewSchedulerAgent

app = Flask(__name__)
CORS(app)

# Initialize the job screening system
jd_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'Dataset', 'job_description.csv')
cv_folder_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'Dataset', 'CVs1')
db_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'recruitment.db')

# Create system instance
system = JobScreeningSystem(db_path=db_path)

@app.route('/api/initialize', methods=['POST'])
def initialize_system():
    """Initialize the system with job descriptions and CVs"""
    try:
        system.initialize(jd_path, cv_folder_path)
        return jsonify({
            'success': True,
            'message': 'System initialized successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/process-jobs', methods=['POST'])
def process_jobs():
    """Process all jobs with the specified threshold"""
    try:
        data = request.json
        threshold = data.get('threshold', 0.75)
        
        system.process_all_jobs(matching_threshold=threshold)
        
        return jsonify({
            'success': True,
            'message': 'Jobs processed successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all job descriptions"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, title, summary, description, required_skills, experience, qualifications, responsibilities
        FROM job_descriptions
        ORDER BY title
        """)
        
        jobs = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts and parse JSON fields
        job_list = []
        for job in jobs:
            job_dict = dict(job)
            
            # Parse JSON fields
            for field in ['required_skills', 'experience', 'qualifications', 'responsibilities']:
                if job_dict[field]:
                    job_dict[field] = json.loads(job_dict[field])
                else:
                    job_dict[field] = []
            
            job_list.append(job_dict)
        
        return jsonify({
            'success': True,
            'jobs': job_list
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """Get all candidates"""
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, name, email, skills, experience, education, certifications
        FROM candidates
        ORDER BY name
        """)
        
        candidates = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts and parse JSON fields
        candidate_list = []
        for candidate in candidates:
            candidate_dict = dict(candidate)
            
            # Parse JSON fields
            for field in ['skills', 'experience', 'education', 'certifications']:
                if candidate_dict[field]:
                    candidate_dict[field] = json.loads(candidate_dict[field])
                else:
                    candidate_dict[field] = []
            
            candidate_list.append(candidate_dict)
        
        return jsonify({
            'success': True,
            'candidates': candidate_list
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/job/<int:job_id>/matches', methods=['GET'])
def get_job_matches(job_id):
    """Get all matches for a specific job"""
    try:
        results = system.get_match_results(job_id)
        
        return jsonify({
            'success': True,
            'matches': results
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/job/<int:job_id>/shortlisted', methods=['GET'])
def get_shortlisted(job_id):
    """Get shortlisted candidates for a job"""
    try:
        # Create a new instance to access the method
        matcher = CandidateMatcherAgent(db_path)
        shortlisted = matcher.get_shortlisted_candidates(job_id)
        
        return jsonify({
            'success': True,
            'shortlisted': shortlisted
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/job/<int:job_id>/schedule-interviews', methods=['POST'])
def schedule_interviews(job_id):
    """Schedule interviews for shortlisted candidates"""
    try:
        data = request.json
        days_ahead = data.get('days_ahead', 7)
        
        # Create a new instance to access the method
        scheduler = InterviewSchedulerAgent(db_path)
        scheduler.schedule_interviews(job_id, days_ahead)
        
        return jsonify({
            'success': True,
            'message': 'Interviews scheduled successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/matches', methods=['GET'])
def get_all_matches():
    """Get all match results"""
    try:
        results = system.get_match_results()
        
        return jsonify({
            'success': True,
            'matches': results
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count jobs
        cursor.execute("SELECT COUNT(*) FROM job_descriptions")
        job_count = cursor.fetchone()[0]
        
        # Count candidates
        cursor.execute("SELECT COUNT(*) FROM candidates")
        candidate_count = cursor.fetchone()[0]
        
        # Count matches
        cursor.execute("SELECT COUNT(*) FROM match_results")
        match_count = cursor.fetchone()[0]
        
        # Count shortlisted candidates
        cursor.execute("SELECT COUNT(*) FROM match_results WHERE shortlisted = 1")
        shortlisted_count = cursor.fetchone()[0]
        
        # Count scheduled interviews
        cursor.execute("SELECT COUNT(*) FROM match_results WHERE interview_sent = 1")
        interview_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'jobs': job_count,
                'candidates': candidate_count,
                'matches': match_count,
                'shortlisted': shortlisted_count,
                'interviews': interview_count
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)