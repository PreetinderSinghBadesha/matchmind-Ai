import os
import pandas as pd
import sqlite3
import PyPDF2
import re
import json
import random
from datetime import datetime, timedelta
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Download necessary NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4') 

# Initialize database
def init_database():
    conn = sqlite3.connect('recruitment.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_descriptions (
        id INTEGER PRIMARY KEY,
        title TEXT,
        description TEXT,
        summary TEXT,
        required_skills TEXT,
        experience TEXT,
        qualifications TEXT,
        responsibilities TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        cv_path TEXT,
        parsed_cv TEXT,
        education TEXT,
        experience TEXT,
        skills TEXT,
        certifications TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS match_results (
        id INTEGER PRIMARY KEY,
        job_id INTEGER,
        candidate_id INTEGER,
        match_score REAL,
        shortlisted INTEGER,
        interview_sent INTEGER,
        interview_time TEXT,
        FOREIGN KEY (job_id) REFERENCES job_descriptions(id),
        FOREIGN KEY (candidate_id) REFERENCES candidates(id)
    )
    ''')
    
    conn.commit()
    conn.close()


# Agent 1: Job Description Summarizer
class JDSummarizerAgent:
    def __init__(self, db_path='recruitment.db'):
        self.db_path = db_path
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def load_job_descriptions(self, jd_file_path):
        """Load job descriptions from CSV file"""
        try:
            # Try different encodings with explicit error handling
            encodings = ['utf-8', 'latin1', 'cp1252', 'ISO-8859-1']
            df = None
            
            for encoding in encodings:
                try:
                    # Add error_bad_lines=False (skipinitialspace for possible CSV formatting issues)
                    df = pd.read_csv(jd_file_path, encoding=encoding, skipinitialspace=True, 
                                     on_bad_lines='skip')
                    print(f"Successfully loaded file with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    print(f"Failed to decode with {encoding}, trying next encoding...")
                    continue
                except Exception as e:
                    print(f"Error with {encoding}: {e}")
                    continue
            
            if df is None:
                raise ValueError("Could not decode file with any of the attempted encodings")
            
            # Clean the data to handle potential special characters
            df['Job Title'] = df['Job Title'].str.strip().fillna('Untitled Position')
            df['Job Description'] = df['Job Description'].str.strip().fillna('No description available')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                try:
                    title = str(row['Job Title'])
                    description = str(row['Job Description'])
                    
                    # Check if job already exists
                    cursor.execute("SELECT id FROM job_descriptions WHERE title = ?", (title,))
                    result = cursor.fetchone()
                    
                    if not result:
                        # Process and summarize the job description
                        summary, skills, exp, qualifications, responsibilities = self.summarize_job_description(description)
                        
                        cursor.execute('''
                        INSERT INTO job_descriptions (title, description, summary, required_skills, 
                                                     experience, qualifications, responsibilities)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (title, description, summary, json.dumps(skills), 
                              json.dumps(exp), json.dumps(qualifications), json.dumps(responsibilities)))
                except Exception as e:
                    print(f"Error processing job: {e}")
                    continue
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error loading job descriptions: {e}")
            return False
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # Tokenize
        tokens = word_tokenize(text)
        # Remove stopwords and lemmatize
        processed_tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        return ' '.join(processed_tokens)
    
    def summarize_job_description(self, description):
        """Extract key elements from job description"""
        # Preprocessing
        processed_text = self.preprocess_text(description)
        
        # Identify sections using regex patterns
        skills_pattern = r'skills|requirements|proficiency|knowledge'
        experience_pattern = r'experience|years|background'
        qualifications_pattern = r'qualifications|education|degree|certification'
        responsibilities_pattern = r'responsibilities|duties|tasks|role'
        
        # Extract skills
        skills = []
        skills_section = re.search(f'.*({skills_pattern}).*', processed_text, re.IGNORECASE)
        if skills_section:
            skills_text = processed_text[skills_section.start():]
            # Extract keywords using TF-IDF
            vectorizer = TfidfVectorizer(max_features=20)
            tfidf_matrix = vectorizer.fit_transform([skills_text])
            feature_names = vectorizer.get_feature_names_out()
            skills = [feature_names[i] for i in tfidf_matrix.toarray()[0].argsort()[-10:][::-1]]
        
        # Similar extraction for other sections
        experience = self.extract_experience(processed_text)
        qualifications = self.extract_qualifications(processed_text)
        responsibilities = self.extract_responsibilities(processed_text)
        
        # Create summary
        summary = f"This job requires skills in {', '.join(skills[:5])}. "
        if experience:
            summary += f"Experience needed: {', '.join(experience[:3])}. "
        if qualifications:
            summary += f"Qualifications: {', '.join(qualifications[:3])}. "
        
        return summary, skills, experience, qualifications, responsibilities
    
    def extract_experience(self, text):
        experience = []
        exp_section = re.search(r'experience|years|background', text, re.IGNORECASE)
        if exp_section:
            exp_text = text[exp_section.start():][:200]  # Take a reasonable chunk
            # Look for years of experience
            years = re.findall(r'\d+\+?\s*(?:year|yr)s?', exp_text)
            experience.extend(years)
            
            # Extract key experience phrases
            exp_phrases = re.findall(r'\w+\s+experience', exp_text)
            experience.extend(exp_phrases)
        
        return experience
    
    def extract_qualifications(self, text):
        qualifications = []
        qual_section = re.search(r'qualifications|education|degree|certification', text, re.IGNORECASE)
        if qual_section:
            qual_text = text[qual_section.start()][:300]
            
            # Look for degrees
            degrees = re.findall(r"bachelor'?s?|master'?s?|phd|doctorate|degree", qual_text, re.IGNORECASE)
            qualifications.extend([d.lower() for d in degrees])
            
            # Look for fields of study
            fields = re.findall(r"(?:in|of)\s+([a-z]+(?:\s+[a-z]+){0,2})", qual_text)
            qualifications.extend([f.lower() for f in fields if len(f) > 3])
        
        return qualifications
    
    def extract_responsibilities(self, text):
        responsibilities = []
        resp_section = re.search(r'responsibilities|duties|tasks|role', text, re.IGNORECASE)
        if resp_section:
            resp_text = text[resp_section.start():][:500]
            
            # Extract sentences or phrases
            sentences = re.split(r'[.;]', resp_text)
            responsibilities = [s.strip() for s in sentences if len(s) > 10][:5]
        
        return responsibilities


# Agent 2: CV Parsing and Recruiting Agent
class CVParsingAgent:
    def __init__(self, db_path='recruitment.db'):
        self.db_path = db_path
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
    
    def load_and_parse_cvs(self, cv_folder_path):
        """Load and parse all CVs from a folder"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for filename in os.listdir(cv_folder_path):
                if filename.endswith('.pdf'):
                    cv_path = os.path.join(cv_folder_path, filename)
                    
                    # Extract candidate ID from filename (assuming format like C1234.pdf)
                    candidate_id = os.path.splitext(filename)[0]
                    
                    # Check if candidate already exists
                    cursor.execute("SELECT id FROM candidates WHERE cv_path = ?", (cv_path,))
                    result = cursor.fetchone()
                    
                    if not result:
                        # Parse the CV
                        cv_text = self.extract_text_from_pdf(cv_path)
                        name, email = self.extract_personal_info(cv_text)
                        education = json.dumps(self.extract_education(cv_text))
                        experience = json.dumps(self.extract_experience(cv_text))
                        skills = json.dumps(self.extract_skills(cv_text))
                        certifications = json.dumps(self.extract_certifications(cv_text))
                        
                        cursor.execute('''
                        INSERT INTO candidates (name, email, cv_path, parsed_cv, 
                                              education, experience, skills, certifications)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (name, email, cv_path, cv_text, 
                              education, experience, skills, certifications))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error parsing CVs: {e}")
            return False
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
        
        return text
    
    def extract_personal_info(self, text):
        """Extract name and email from CV"""
        # Simple name extraction (could be improved)
        name = "Unknown"
        name_match = re.search(r'^([A-Z][a-z]+ [A-Z][a-z]+)', text)
        if name_match:
            name = name_match.group(1)
        
        # Email extraction
        email = "unknown@example.com"
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        if email_match:
            email = email_match.group(0)
        
        return name, email
    
    def extract_education(self, text):
        """Extract education information"""
        education = []
        
        # Look for education section
        edu_section = re.search(r'(?i)education|academic|qualification', text)
        if edu_section:
            edu_text = text[edu_section.start():edu_section.start() + 1000]  # Take a chunk after the heading
            
            # Look for degree patterns
            degrees = re.findall(r'(?i)(?:bachelor|master|phd|doctorate|b\.?(?:sc|a|tech)|m\.?(?:sc|a|tech)|degree)', edu_text)
            
            # Look for universities/colleges
            universities = re.findall(r'(?i)(?:university|college|institute|school) of [a-z ]+', edu_text)
            
            # Look for years
            years = re.findall(r'(?:19|20)\d{2}(?:\s*-\s*(?:present|(?:19|20)\d{2}))?', edu_text)
            
            # Combine information
            for i in range(max(len(degrees), len(universities))):
                degree = degrees[i] if i < len(degrees) else ""
                university = universities[i] if i < len(universities) else ""
                year = years[i] if i < len(years) else ""
                
                if degree or university:
                    education.append({
                        "degree": degree,
                        "institution": university,
                        "year": year
                    })
        
        return education
    
    def extract_experience(self, text):
        """Extract work experience"""
        experience = []
        
        # Find experience section
        exp_section = re.search(r'(?i)experience|employment|work history', text)
        if exp_section:
            exp_text = text[exp_section.start():]
            
            # Look for company names (could be improved)
            companies = re.findall(r'(?i)(?:at|with|for)\s+([A-Z][a-z]+(?: [A-Z][a-z]+){0,3})', exp_text)
            
            # Look for job titles
            titles = re.findall(r'(?i)(?:senior|junior|lead)?\s*(?:developer|engineer|analyst|manager|designer|administrator)', exp_text)
            
            # Look for date ranges
            dates = re.findall(r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\s*(?:-|–|to)\s*(?:Present|Current|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})', exp_text)
            
            # Combine information
            for i in range(max(len(companies), len(titles), len(dates))):
                company = companies[i][0] if i < len(companies) else ""
                title = titles[i] if i < len(titles) else ""
                date = dates[i] if i < len(dates) else ""
                
                if company or title:
                    experience.append({
                        "company": company,
                        "title": title,
                        "period": date
                    })
        
        return experience
    
    def extract_skills(self, text):
        """Extract skills from CV"""
        skills = []
        
        # Common technical skills
        tech_skills = [
            "python", "java", "javascript", "c\\+\\+", "sql", "nosql", "aws", "azure",
            "php", "html", "css", "react", "angular", "vue", "node", "express", 
            "django", "flask", "spring", "hibernate", "docker", "kubernetes",
            "git", "jenkins", "ci/cd", "agile", "scrum", "tensorflow", "pytorch",
            "machine learning", "artificial intelligence", "data science", "nlp",
            "network", "security", "linux", "windows", "macos", "unix"
        ]
        
        # Look for skills section
        skills_section = re.search(r'(?i)(?:technical |key |core )?skills|technologies|languages|tools', text)
        if skills_section:
            skills_text = text[skills_section.start():skills_section.start() + 1000]
            
            # Match skills from our predefined list
            for skill in tech_skills:
                if re.search(r'\b' + skill + r'\b', skills_text, re.IGNORECASE):
                    skills.append(skill)
            
            # Also look for anything between commas in the skills section
            comma_skills = re.findall(r'([^,]+),', skills_text)
            for skill in comma_skills:
                cleaned_skill = skill.strip()
                if 2 < len(cleaned_skill) < 25 and cleaned_skill.lower() not in [s.lower() for s in skills]:
                    skills.append(cleaned_skill)
        
        return skills
    
    def extract_certifications(self, text):
        """Extract certifications from CV"""
        certifications = []
        
        # Look for certifications section
        cert_section = re.search(r'(?i)certifications?|qualifications|accreditations', text)
        if cert_section:
            cert_text = text[cert_section.start():cert_section.start() + 500]
            
            # Common certification keywords
            cert_keywords = [
                "certified", "certificate", "certification", "aws", "microsoft", 
                "cisco", "oracle", "comptia", "pmp", "itil", "scrum", "professional"
            ]
            
            # Extract certification patterns
            for keyword in cert_keywords:
                matches = re.findall(r'(?i)' + keyword + r'[^.]*', cert_text)
                for match in matches:
                    if 10 < len(match) < 100:  # Reasonable certification name length
                        match = match.strip()
                        if match not in certifications:
                            certifications.append(match)
        
        return certifications


# Agent 3: Candidate-Job Matcher
class CandidateMatcherAgent:
    def __init__(self, db_path='recruitment.db'):
        self.db_path = db_path
        self.threshold = 0.8  # Default matching threshold
        
    def set_threshold(self, threshold):
        """Set the matching threshold (0.0-1.0)"""
        if 0.0 <= threshold <= 1.0:
            self.threshold = threshold
            return True
        return False
    
    def match_candidates_to_job(self, job_id):
        """Match all candidates to a specific job"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get job details
        cursor.execute("""
        SELECT id, title, required_skills, experience, qualifications, responsibilities
        FROM job_descriptions
        WHERE id = ?
        """, (job_id,))
        
        job = cursor.fetchone()
        if not job:
            print(f"No job found with ID {job_id}")
            conn.close()
            return False
        
        # Load job requirements
        job_skills = json.loads(job['required_skills']) if job['required_skills'] else []
        job_experience = json.loads(job['experience']) if job['experience'] else []
        job_qualifications = json.loads(job['qualifications']) if job['qualifications'] else []
        
        # Get all candidates
        cursor.execute("""
        SELECT id, name, skills, experience, education, certifications
        FROM candidates
        """)
        
        candidates = cursor.fetchall()
        
        for candidate in candidates:
            # Load candidate qualifications
            candidate_skills = json.loads(candidate['skills']) if candidate['skills'] else []
            candidate_experience = json.loads(candidate['experience']) if candidate['experience'] else []
            candidate_education = json.loads(candidate['education']) if candidate['education'] else []
            candidate_certifications = json.loads(candidate['certifications']) if candidate['certifications'] else []
            
            # Calculate match score
            score = self.calculate_match_score(
                job_skills, job_experience, job_qualifications,
                candidate_skills, candidate_experience, candidate_education, candidate_certifications
            )
            
            # Check if match already exists
            cursor.execute("""
            SELECT id FROM match_results
            WHERE job_id = ? AND candidate_id = ?
            """, (job_id, candidate['id']))
            
            match_exists = cursor.fetchone()
            
            # Insert or update match results
            shortlisted = 1 if score >= self.threshold else 0
            
            if match_exists:
                cursor.execute("""
                UPDATE match_results
                SET match_score = ?, shortlisted = ?
                WHERE job_id = ? AND candidate_id = ?
                """, (score, shortlisted, job_id, candidate['id']))
            else:
                cursor.execute("""
                INSERT INTO match_results (job_id, candidate_id, match_score, shortlisted, interview_sent)
                VALUES (?, ?, ?, ?, 0)
                """, (job_id, candidate['id'], score, shortlisted))
        
        conn.commit()
        conn.close()
        return True
    
    def calculate_match_score(self, job_skills, job_experience, job_qualifications,
                              candidate_skills, candidate_experience, candidate_education, candidate_certifications):
        """Calculate a match score between a candidate and job"""
        # Skills match (50% weight)
        skills_score = 0
        if job_skills and candidate_skills:
            matched_skills = 0
            for job_skill in job_skills:
                if any(job_skill.lower() in cand_skill.lower() for cand_skill in candidate_skills):
                    matched_skills += 1
            
            if job_skills:
                skills_score = matched_skills / len(job_skills)
        
        # Experience match (30% weight)
        experience_score = 0
        if candidate_experience:
            # Simple experience match - can be improved
            experience_score = min(1.0, len(candidate_experience) / 2)  # Assume 2+ experiences is good
        
        # Education/qualifications match (20% weight)
        edu_score = 0
        if job_qualifications and candidate_education:
            # Check for degree matches
            matched_quals = 0
            for job_qual in job_qualifications:
                for edu in candidate_education:
                    if job_qual.lower() in edu.get('degree', '').lower():
                        matched_quals += 1
                        break
            
            if job_qualifications:
                edu_score = matched_quals / len(job_qualifications)
        
        # Bonus for certifications (up to 10% bonus)
        cert_bonus = min(0.1, len(candidate_certifications) * 0.02)
        
        # Calculate weighted score
        final_score = (0.5 * skills_score) + (0.3 * experience_score) + (0.2 * edu_score) + cert_bonus
        
        # Cap at 1.0
        return min(1.0, final_score)
    
    def get_shortlisted_candidates(self, job_id):
        """Get all shortlisted candidates for a job"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT c.id, c.name, c.email, m.match_score
        FROM candidates c
        JOIN match_results m ON c.id = m.candidate_id
        WHERE m.job_id = ? AND m.shortlisted = 1 AND m.interview_sent = 0
        ORDER BY m.match_score DESC
        """, (job_id,))
        
        shortlisted = cursor.fetchall()
        conn.close()
        
        return [dict(candidate) for candidate in shortlisted]


# Agent 4: Interview Scheduler
class InterviewSchedulerAgent:
    def __init__(self, db_path='recruitment.db'):
        self.db_path = db_path
    
    def schedule_interviews(self, job_id, days_ahead=7):
        """Schedule interviews for shortlisted candidates"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get job details
        cursor.execute("SELECT title FROM job_descriptions WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        if not job:
            print(f"No job found with ID {job_id}")
            conn.close()
            return False
        
        # Get shortlisted candidates who haven't been sent an interview request yet
        cursor.execute("""
        SELECT c.id, c.name, c.email, m.id as match_id
        FROM candidates c
        JOIN match_results m ON c.id = m.candidate_id
        WHERE m.job_id = ? AND m.shortlisted = 1 AND m.interview_sent = 0
        """, (job_id,))
        
        candidates = cursor.fetchall()
        
        # Schedule interviews
        for candidate in candidates:
            # Generate interview datetime (within next 7 days)
            interview_date = datetime.now() + timedelta(days=random.randint(1, days_ahead))
            interview_hour = random.randint(9, 16)  # Between 9 AM and 4 PM
            interview_minute = random.choice([0, 15, 30, 45])
            
            interview_datetime = interview_date.replace(
                hour=interview_hour, 
                minute=interview_minute,
                second=0, 
                microsecond=0
            )
            
            # Format for storage
            interview_time = interview_datetime.strftime("%Y-%m-%d %H:%M")
            
            # Generate email
            email_content = self.generate_interview_email(
                candidate['name'],
                job['title'],
                interview_datetime
            )
            
            # In a real system, we would send the email here
            # For this demo, we'll just mark it as sent in the database
            
            # Update database
            cursor.execute("""
            UPDATE match_results
            SET interview_sent = 1, interview_time = ?
            WHERE id = ?
            """, (interview_time, candidate['match_id']))
            
            # For demonstration purposes, print the email that would be sent
            print(f"Email sent to {candidate['email']}:")
            print(email_content)
            print("-" * 50)
        
        conn.commit()
        conn.close()
        return True
    
    def generate_interview_email(self, candidate_name, job_title, interview_datetime):
        """Generate a personalized interview email"""
        # Format the datetime for display
        date_str = interview_datetime.strftime("%A, %B %d, %Y")
        time_str = interview_datetime.strftime("%I:%M %p")
        
        # Create email content
        subject = f"Interview Invitation for {job_title} Position"
        
        body = f"""Dear {candidate_name},

We are pleased to inform you that your application for the {job_title} position has been shortlisted. We would like to invite you for an interview to further discuss your qualifications and experience.

Interview Details:
- Position: {job_title}
- Date: {date_str}
- Time: {time_str}
- Format: Video Conference (Zoom link will be provided 24 hours before the interview)

Please confirm your availability for this interview by replying to this email. If this time doesn't work for you, please suggest a few alternative times within the next week.

Before the interview, we recommend that you:
1. Research our company and the role
2. Review your resume and be prepared to discuss your experience
3. Prepare questions you might have about the position or company

We're looking forward to speaking with you!

Best regards,
HR Team
MatchMind AI Recruitment
"""
        
        # In a real implementation, this would create an actual email
        email = MIMEMultipart()
        email['Subject'] = subject
        email.attach(MIMEText(body, 'plain'))
        
        return email.as_string()


# Main class to orchestrate the multi-agent system
class JobScreeningSystem:
    def __init__(self, db_path='recruitment.db'):
        self.db_path = db_path
        self.jd_agent = JDSummarizerAgent(db_path)
        self.cv_agent = CVParsingAgent(db_path)
        self.matcher_agent = CandidateMatcherAgent(db_path)
        self.scheduler_agent = InterviewSchedulerAgent(db_path)
    
    def initialize(self, jd_path, cv_folder_path):
        """Initialize the system with job descriptions and CVs"""
        print("Initializing database...")
        init_database()
        
        print("Loading job descriptions...")
        self.jd_agent.load_job_descriptions(jd_path)
        
        print("Loading and parsing CVs...")
        self.cv_agent.load_and_parse_cvs(cv_folder_path)
        
        print("System initialized successfully!")
    
    def process_all_jobs(self, matching_threshold=0.8):
        """Process all jobs and candidates"""
        self.matcher_agent.set_threshold(matching_threshold)
        
        # Get all jobs from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM job_descriptions")
        jobs = cursor.fetchall()
        conn.close()
        
        # Process each job
        for job in jobs:
            job_id = job[0]
            print(f"Processing job ID {job_id}...")
            
            # Match candidates to this job
            self.matcher_agent.match_candidates_to_job(job_id)
            
            # Schedule interviews for shortlisted candidates
            shortlisted = self.matcher_agent.get_shortlisted_candidates(job_id)
            print(f"Found {len(shortlisted)} shortlisted candidates for job ID {job_id}")
            
            # Send interview requests
            self.scheduler_agent.schedule_interviews(job_id)
    
    def get_match_results(self, job_id=None):
        """Get match results, optionally filtered by job ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if job_id:
            cursor.execute("""
            SELECT j.title as job_title, c.name as candidate_name, m.match_score, m.shortlisted, 
                   m.interview_sent, m.interview_time
            FROM match_results m
            JOIN job_descriptions j ON m.job_id = j.id
            JOIN candidates c ON m.candidate_id = c.id
            WHERE m.job_id = ?
            ORDER BY m.match_score DESC
            """, (job_id,))
        else:
            cursor.execute("""
            SELECT j.title as job_title, c.name as candidate_name, m.match_score, m.shortlisted, 
                   m.interview_sent, m.interview_time
            FROM match_results m
            JOIN job_descriptions j ON m.job_id = j.id
            JOIN candidates c ON m.candidate_id = c.id
            ORDER BY j.title, m.match_score DESC
            """)
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]


# Main execution function
def main():
    # Paths to data
    jd_path = "Dataset/job_description.csv"
    cv_folder_path = "Dataset/CVs1"
    
    # Initialize system
    system = JobScreeningSystem()
    system.initialize(jd_path, cv_folder_path)
    
    # Process all jobs with 75% threshold
    system.process_all_jobs(matching_threshold=0.75)
    
    # Print some results
    print("\nMatch Results Summary:")
    results = system.get_match_results()
    
    # Group by job
    jobs = {}
    for result in results:
        job_title = result['job_title']
        if job_title not in jobs:
            jobs[job_title] = []
        jobs[job_title].append(result)
    
    # Print summary for each job
    for job_title, candidates in jobs.items():
        shortlisted = [c for c in candidates if c['shortlisted'] == 1]
        interviews = [c for c in candidates if c['interview_sent'] == 1]
        
        print(f"\nJob: {job_title}")
        print(f"Total candidates: {len(candidates)}")
        print(f"Shortlisted: {len(shortlisted)}")
        print(f"Interviews scheduled: {len(interviews)}")
        
        if interviews:
            print("\nTop 3 candidates with scheduled interviews:")
            for i, candidate in enumerate(interviews[:3]):
                print(f"{i+1}. {candidate['candidate_name']} (Score: {candidate['match_score']:.2f}, Interview: {candidate['interview_time']})")


if __name__ == "__main__":
    main()