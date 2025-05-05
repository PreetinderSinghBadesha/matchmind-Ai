import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

function JobDetails({ refreshStats }) {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [schedulingInterviews, setSchedulingInterviews] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    const fetchJobAndMatches = async () => {
      try {
        setLoading(true);
        // Fetch job details
        const jobResponse = await fetch(`http://localhost:5000/api/jobs`);
        const jobData = await jobResponse.json();
        
        if (jobData.success) {
          const foundJob = jobData.jobs.find(j => j.id === parseInt(id));
          if (foundJob) {
            setJob(foundJob);
          } else {
            setError('Job not found');
          }
        } else {
          setError(jobData.message || 'Failed to fetch job details');
        }
        
        // Fetch matches for this job
        const matchesResponse = await fetch(`http://localhost:5000/api/job/${id}/matches`);
        const matchesData = await matchesResponse.json();
        
        if (matchesData.success) {
          setMatches(matchesData.matches);
        } else {
          console.error('Error fetching matches:', matchesData.message);
        }
      } catch (error) {
        setError('Error connecting to server');
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchJobAndMatches();
  }, [id]);

  const handleScheduleInterviews = async () => {
    try {
      setSchedulingInterviews(true);
      setMessage({ type: 'info', text: 'Scheduling interviews...' });
      
      const response = await fetch(`http://localhost:5000/api/job/${id}/schedule-interviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ days_ahead: 7 })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setMessage({ type: 'success', text: 'Interviews scheduled successfully!' });
        
        // Refresh matches and stats
        const matchesResponse = await fetch(`http://localhost:5000/api/job/${id}/matches`);
        const matchesData = await matchesResponse.json();
        
        if (matchesData.success) {
          setMatches(matchesData.matches);
        }
        
        refreshStats();
      } else {
        setMessage({ type: 'danger', text: `Error: ${data.message}` });
      }
    } catch (error) {
      setMessage({ type: 'danger', text: `Error: ${error.message}` });
    } finally {
      setSchedulingInterviews(false);
    }
  };
  
  if (loading) {
    return <div className="d-flex justify-content-center mt-5"><div className="spinner-border" role="status"></div></div>;
  }

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  if (!job) {
    return <div className="alert alert-warning">Job not found</div>;
  }

  const shortlistedCandidates = matches.filter(match => match.shortlisted === 1);
  const interviewsSent = matches.filter(match => match.interview_sent === 1);

  return (
    <div className="job-details">
      <nav aria-label="breadcrumb">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/jobs">Jobs</Link></li>
          <li className="breadcrumb-item active" aria-current="page">{job.title}</li>
        </ol>
      </nav>

      {message && (
        <div className={`alert alert-${message.type}`} role="alert">
          {message.text}
        </div>
      )}

      <div className="card mb-4">
        <div className="card-header">
          <h2>{job.title}</h2>
        </div>
        <div className="card-body">
          <h5>Summary</h5>
          <p className="lead">{job.summary}</p>
          
          <hr />
          
          <h5>Description</h5>
          <p style={{ whiteSpace: 'pre-line' }}>{job.description}</p>
          
          <div className="row mt-4">
            <div className="col-md-4">
              <h5>Required Skills</h5>
              <ul className="list-group">
                {job.required_skills.map((skill, index) => (
                  <li key={index} className="list-group-item">{skill}</li>
                ))}
              </ul>
            </div>
            
            <div className="col-md-4">
              <h5>Experience</h5>
              <ul className="list-group">
                {job.experience.length > 0 ? (
                  job.experience.map((exp, index) => (
                    <li key={index} className="list-group-item">{exp}</li>
                  ))
                ) : (
                  <li className="list-group-item">No specific experience listed</li>
                )}
              </ul>
            </div>
            
            <div className="col-md-4">
              <h5>Qualifications</h5>
              <ul className="list-group">
                {job.qualifications.length > 0 ? (
                  job.qualifications.map((qual, index) => (
                    <li key={index} className="list-group-item">{qual}</li>
                  ))
                ) : (
                  <li className="list-group-item">No specific qualifications listed</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <div className="card mb-4">
        <div className="card-header d-flex justify-content-between align-items-center">
          <h4 className="mb-0">Matched Candidates</h4>
          <div>
            <button 
              className="btn btn-success" 
              onClick={handleScheduleInterviews} 
              disabled={schedulingInterviews || shortlistedCandidates.length === 0 || shortlistedCandidates.length === interviewsSent.length}
            >
              {schedulingInterviews ? 'Scheduling...' : 'Schedule Interviews'}
            </button>
          </div>
        </div>
        <div className="card-body">
          <div className="row mb-3">
            <div className="col">
              <div className="card bg-light">
                <div className="card-body">
                  <h5>Total Matches: {matches.length}</h5>
                  <h5>Shortlisted: {shortlistedCandidates.length}</h5>
                  <h5>Interviews Sent: {interviewsSent.length}</h5>
                </div>
              </div>
            </div>
          </div>
          
          {matches.length === 0 ? (
            <div className="alert alert-info">
              No candidates have been matched to this job yet. Try processing jobs from the dashboard.
            </div>
          ) : (
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Match Score</th>
                  <th>Status</th>
                  <th>Interview Time</th>
                </tr>
              </thead>
              <tbody>
                {matches.sort((a, b) => b.match_score - a.match_score).map((match) => (
                  <tr key={match.candidate_name}>
                    <td>
                      <Link to={`/candidates/${match.candidate_id}`}>
                        {match.candidate_name}
                      </Link>
                    </td>
                    <td>
                      <div className="progress">
                        <div 
                          className={`progress-bar ${match.match_score >= 0.8 ? 'bg-success' : match.match_score >= 0.6 ? 'bg-info' : 'bg-warning'}`} 
                          role="progressbar" 
                          style={{ width: `${match.match_score * 100}%` }}
                          aria-valuenow={match.match_score * 100} 
                          aria-valuemin="0" 
                          aria-valuemax="100"
                        >
                          {(match.match_score * 100).toFixed(0)}%
                        </div>
                      </div>
                    </td>
                    <td>
                      {match.shortlisted ? (
                        match.interview_sent ? (
                          <span className="badge bg-success">Interview Scheduled</span>
                        ) : (
                          <span className="badge bg-warning">Shortlisted</span>
                        )
                      ) : (
                        <span className="badge bg-secondary">Not Shortlisted</span>
                      )}
                    </td>
                    <td>
                      {match.interview_time || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

export default JobDetails;