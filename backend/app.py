from flask import Flask, request, jsonify
import sys
import os
from flask_cors import CORS
import json
import sqlite3
import tempfile
import uuid

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

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    """Upload a resume and find matching jobs"""
    try:
        # Check if a file was uploaded
        if 'resume' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file uploaded'
            }), 400
        
        resume_file = request.files['resume']
        
        # Check if the file is valid
        if resume_file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
            
        if not resume_file.filename.lower().endswith('.pdf'):
            return jsonify({
                'success': False,
                'message': 'Only PDF files are allowed'
            }), 400
        
        # Save the uploaded file to a temporary location
        temp_dir = tempfile.gettempdir()
        unique_filename = f"{uuid.uuid4()}.pdf"
        temp_filepath = os.path.join(temp_dir, unique_filename)
        
        resume_file.save(temp_filepath)
        
        # Parse the resume
        cv_agent = CVParsingAgent(db_path)
        cv_text = cv_agent.extract_text_from_pdf(temp_filepath)
        
        # Extract information from the resume
        name, email = cv_agent.extract_personal_info(cv_text)
        education = cv_agent.extract_education(cv_text)
        experience = cv_agent.extract_experience(cv_text)
        skills = cv_agent.extract_skills(cv_text)
        certifications = cv_agent.extract_certifications(cv_text)
        
        # Connect to the database to get all jobs
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT id, title, required_skills, experience, qualifications, responsibilities
        FROM job_descriptions
        """)
        
        jobs = cursor.fetchall()
        
        # Calculate match scores for all jobs
        matcher = CandidateMatcherAgent(db_path)
        matches = []
        
        for job in jobs:
            # Parse job requirements
            job_skills = json.loads(job['required_skills']) if job['required_skills'] else []
            job_experience = json.loads(job['experience']) if job['experience'] else []
            job_qualifications = json.loads(job['qualifications']) if job['qualifications'] else []
            
            # Calculate match score
            match_score = matcher.calculate_match_score(
                job_skills, job_experience, job_qualifications,
                skills, experience, education, certifications
            )
            
            # Add to results if score is reasonable (e.g., > 0.3)
            if match_score > 0.3:
                matches.append({
                    'job_id': job['id'],
                    'job_title': job['title'],
                    'match_score': match_score
                })
        
        # Clean up the temporary file
        try:
            os.remove(temp_filepath)
        except:
            pass
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Resume processed successfully',
            'candidate': {
                'name': name,
                'email': email,
                'skills': skills,
                'education': education,
                'experience': experience,
                'certifications': certifications
            },
            'matches': matches
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"Error processing resume: {str(e)}"
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