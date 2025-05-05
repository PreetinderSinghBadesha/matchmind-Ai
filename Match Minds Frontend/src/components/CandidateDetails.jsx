import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

function CandidateDetails() {
  const { id } = useParams();
  const [candidate, setCandidate] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCandidateAndMatches = async () => {
      try {
        setLoading(true);
        // Fetch candidate details
        const candidateResponse = await fetch(`http://localhost:5000/api/candidates`);
        const candidateData = await candidateResponse.json();
        
        if (candidateData.success) {
          const foundCandidate = candidateData.candidates.find(c => c.id === parseInt(id));
          if (foundCandidate) {
            setCandidate(foundCandidate);
          } else {
            setError('Candidate not found');
          }
        } else {
          setError(candidateData.message || 'Failed to fetch candidate details');
        }
        
        // Fetch match results
        const matchesResponse = await fetch(`http://localhost:5000/api/matches`);
        const matchesData = await matchesResponse.json();
        
        if (matchesData.success) {
          // Filter matches for this candidate
          const candidateMatches = matchesData.matches.filter(
            match => match.candidate_id === parseInt(id)
          );
          setMatches(candidateMatches);
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

    fetchCandidateAndMatches();
  }, [id]);

  if (loading) {
    return <div className="d-flex justify-content-center mt-5"><div className="spinner-border" role="status"></div></div>;
  }

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  if (!candidate) {
    return <div className="alert alert-warning">Candidate not found</div>;
  }

  const sortedMatches = [...matches].sort((a, b) => b.match_score - a.match_score);
  const topMatch = sortedMatches.length > 0 ? sortedMatches[0] : null;

  return (
    <div className="candidate-details">
      <nav aria-label="breadcrumb">
        <ol className="breadcrumb">
          <li className="breadcrumb-item"><Link to="/candidates">Candidates</Link></li>
          <li className="breadcrumb-item active" aria-current="page">{candidate.name}</li>
        </ol>
      </nav>

      <div className="card mb-4">
        <div className="card-header">
          <h2>{candidate.name}</h2>
          <p className="text-muted mb-0">{candidate.email}</p>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-md-6">
              <h5>Skills</h5>
              <div className="mb-4">
                {candidate.skills.length > 0 ? (
                  candidate.skills.map((skill, index) => (
                    <span key={index} className="badge bg-info me-2 mb-2">
                      {skill}
                    </span>
                  ))
                ) : (
                  <p>No skills listed</p>
                )}
              </div>

              <h5>Certifications</h5>
              {candidate.certifications.length > 0 ? (
                <ul className="list-group mb-4">
                  {candidate.certifications.map((cert, index) => (
                    <li key={index} className="list-group-item">{cert}</li>
                  ))}
                </ul>
              ) : (
                <p className="mb-4">No certifications listed</p>
              )}
            </div>

            <div className="col-md-6">
              {topMatch && (
                <div className="card bg-light mb-4">
                  <div className="card-body">
                    <h5 className="card-title">Best Job Match</h5>
                    <h6>{topMatch.job_title}</h6>
                    <div className="progress mb-3">
                      <div 
                        className={`progress-bar ${topMatch.match_score >= 0.8 ? 'bg-success' : topMatch.match_score >= 0.6 ? 'bg-info' : 'bg-warning'}`} 
                        role="progressbar" 
                        style={{ width: `${topMatch.match_score * 100}%` }}
                        aria-valuenow={topMatch.match_score * 100} 
                        aria-valuemin="0" 
                        aria-valuemax="100"
                      >
                        {(topMatch.match_score * 100).toFixed(0)}%
                      </div>
                    </div>
                    <p>
                      Status: {topMatch.shortlisted ? (
                        topMatch.interview_sent ? (
                          <span className="badge bg-success">Interview Scheduled</span>
                        ) : (
                          <span className="badge bg-warning">Shortlisted</span>
                        )
                      ) : (
                        <span className="badge bg-secondary">Not Shortlisted</span>
                      )}
                    </p>
                    {topMatch.interview_time && (
                      <p>Interview scheduled for: {topMatch.interview_time}</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          <hr />
          
          <div className="row">
            <div className="col-md-6">
              <h5>Education</h5>
              {candidate.education.length > 0 ? (
                <div className="mb-4">
                  {candidate.education.map((edu, index) => (
                    <div key={index} className="card mb-2">
                      <div className="card-body">
                        <h6>{edu.degree || 'Degree not specified'}</h6>
                        <p className="mb-0">{edu.institution || 'Institution not specified'}</p>
                        <small className="text-muted">{edu.year || 'Year not specified'}</small>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mb-4">No education details listed</p>
              )}
            </div>

            <div className="col-md-6">
              <h5>Work Experience</h5>
              {candidate.experience.length > 0 ? (
                <div className="mb-4">
                  {candidate.experience.map((exp, index) => (
                    <div key={index} className="card mb-2">
                      <div className="card-body">
                        <h6>{exp.title || 'Title not specified'}</h6>
                        <p className="mb-0">{exp.company || 'Company not specified'}</p>
                        <small className="text-muted">{exp.period || 'Period not specified'}</small>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mb-4">No work experience listed</p>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="card mb-4">
        <div className="card-header">
          <h4>Job Matches</h4>
        </div>
        <div className="card-body">
          {matches.length === 0 ? (
            <div className="alert alert-info">
              No job matches found for this candidate. Try processing jobs from the dashboard.
            </div>
          ) : (
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Match Score</th>
                  <th>Status</th>
                  <th>Interview Time</th>
                </tr>
              </thead>
              <tbody>
                {sortedMatches.map((match) => (
                  <tr key={match.job_title}>
                    <td>
                      <Link to={`/jobs/${match.job_id}`}>
                        {match.job_title}
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

export default CandidateDetails;