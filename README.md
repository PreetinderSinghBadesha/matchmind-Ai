# MatchMind AI: Intelligent Job Screening System

![MatchMind AI Logo](https://img.shields.io/badge/MatchMind-AI-4a2bfc)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

MatchMind AI is a multi-agent intelligent system designed to automate and optimize the job screening and candidate matching process for recruiters and HR professionals. It combines natural language processing, machine learning, and data analytics to accurately match candidates to job openings, streamlining the hiring process and improving the quality of candidate selection.

## Key Features

- **Multi-Agent Architecture**: Four specialized AI agents working together:
  - **Job Description Summarizer**: Extracts key requirements and skills from job listings
  - **CV Parsing Agent**: Intelligently extracts candidate qualifications from resumes
  - **Candidate-Job Matcher**: Uses advanced algorithms to score and shortlist candidates
  - **Interview Scheduler**: Automates the interview process for shortlisted candidates

- **Comprehensive Dashboard**: Real-time statistics on jobs, candidates, and matches

- **Smart Matching Algorithm**: 
  - Analyzes skills, experience, education, and certifications
  - Produces accurate match scores between candidates and positions
  - Configurable matching threshold for different hiring needs

- **Automated Interview Scheduling**:
  - Generates personalized interview invitations
  - Schedules optimal interview times
  - Tracks candidate communication status

## System Architecture

### Model Layer
- Python-based AI models for text processing and candidate matching
- SQLite database for persistent storage of jobs, candidates, and matches
- NLTK and scikit-learn for natural language processing and machine learning

### API Backend
- Flask RESTful API exposing the model's functionality
- Endpoints for initializing the system, processing jobs, and managing data
- CORS support for seamless frontend integration

### Frontend Interface
- Modern React application with dynamic components
- Bootstrap-based responsive UI design 
- Interactive data visualization and filtering options

## Screenshots

*(Note: Add screenshots of dashboard, job listings, and candidate matching here)*

## Installation and Setup

### Prerequisites

- Python 3.8+ with pip
- Node.js 14+ with npm
- Git

### Setting Up the Model

```bash
# Clone the repository
git clone https://github.com/your-username/matchmind-ai.git
cd matchmind-ai

# Set up Python virtual environment for the model
cd model
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Download NLTK data (automatically downloaded on first run)
python main.py
```

### Setting Up the Backend API

```bash
# Set up Python virtual environment for the backend
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the Flask server
python app.py
```

### Setting Up the Frontend

```bash
# Install frontend dependencies
cd "../Match Minds Frontend"
npm install

# Install additional required packages
npm install react-router-dom

# Run the development server
npm run dev
```

## Data Preparation

### Job Descriptions
Place your job descriptions in a CSV file with the format:

```
Job Title,Job Description
Software Engineer,"Description: We are seeking a skilled Software Engineer..."
```

Store this file in `model/Dataset/job_description.csv`

### Candidate CVs
Place candidate resumes/CVs in PDF format in the `model/Dataset/CVs1` directory.

## Usage Guide

1. **System Initialization**:
   - Navigate to the "Initialize System" page
   - Click "Initialize System" to load job descriptions and parse CVs

2. **Processing Jobs**:
   - On the Dashboard, set the matching threshold (0.0-1.0)
   - Click "Process Jobs" to analyze and match candidates to jobs

3. **Viewing Results**:
   - Browse jobs and candidates from the respective navigation links
   - View match scores and shortlisted candidates for each job
   - Schedule interviews for qualified candidates

4. **Interview Management**:
   - View scheduled interviews in the job or candidate details pages
   - Check interview status and scheduled times

## Technical Details

### Model Components

- **Natural Language Processing**: Uses NLTK for tokenization, lemmatization, and text processing
- **Feature Extraction**: TF-IDF vectorization for key term identification
- **Matching Algorithm**: Cosine similarity and weighted feature scoring
- **Database Schema**:
  - `job_descriptions`: Stores job listings and extracted requirements
  - `candidates`: Stores candidate information and parsed CV data
  - `match_results`: Stores match scores, shortlisting status, and interview details

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/initialize | POST | Initialize the system with job and CV data |
| /api/process-jobs | POST | Run the matching algorithm with a specified threshold |
| /api/jobs | GET | Retrieve all job listings |
| /api/job/:id | GET | Get details for a specific job |
| /api/job/:id/matches | GET | Get all candidate matches for a job |
| /api/candidates | GET | Retrieve all candidates |
| /api/candidate/:id | GET | Get details for a specific candidate |
| /api/matches | GET | Get all job-candidate matches |

## Performance Optimization

The system is optimized for:
- Efficient text processing with appropriate preprocessing
- Fast candidate-job matching using vectorization
- Minimal database queries through smart caching
- Responsive UI with optimized React components

## Future Enhancements

- Integration with email services for real interview scheduling
- Machine learning model for scoring prediction based on historical hiring data
- Advanced resume parsing with deep learning models
- Integration with calendar systems for automated scheduling
- Mobile application for on-the-go recruitment management

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request