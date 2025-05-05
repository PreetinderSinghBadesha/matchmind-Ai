import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function MatchesList() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // 'all', 'shortlisted', 'interviewed'

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/matches');
        const data = await response.json();
        
        if (data.success) {
          setMatches(data.matches);
        } else {
          setError(data.message || 'Failed to fetch matches');
        }
      } catch (error) {
        setError('Error connecting to server');
        console.error('Error fetching matches:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMatches();
  }, []);

  const filteredMatches = matches.filter(match => {
    if (filter === 'all') return true;
    if (filter === 'shortlisted') return match.shortlisted === 1;
    if (filter === 'interviewed') return match.interview_sent === 1;
    return true;
  });

  const sortedMatches = filteredMatches.sort((a, b) => b.match_score - a.match_score);

  if (loading) {
    return <div className="d-flex justify-content-center mt-5"><div className="spinner-border" role="status"></div></div>;
  }

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  return (
    <div className="matches-list">
      <h1>Job-Candidate Matches</h1>
      <p className="lead">
        All matches between jobs and candidates calculated by the AI system
      </p>

      <div className="mb-4">
        <div className="btn-group" role="group">
          <button 
            type="button" 
            className={`btn ${filter === 'all' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setFilter('all')}
          >
            All Matches
          </button>
          <button 
            type="button" 
            className={`btn ${filter === 'shortlisted' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setFilter('shortlisted')}
          >
            Shortlisted
          </button>
          <button 
            type="button" 
            className={`btn ${filter === 'interviewed' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setFilter('interviewed')}
          >
            Interviews Scheduled
          </button>
        </div>
      </div>
      
      {matches.length === 0 ? (
        <div className="alert alert-info">
          No matches found. Please process jobs from the dashboard first.
        </div>
      ) : filteredMatches.length === 0 ? (
        <div className="alert alert-info">
          No matches found with the current filter.
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-striped table-hover">
            <thead className="table-dark">
              <tr>
                <th>Job Title</th>
                <th>Candidate</th>
                <th>Match Score</th>
                <th>Status</th>
                <th>Interview Time</th>
              </tr>
            </thead>
            <tbody>
              {sortedMatches.map((match, index) => (
                <tr key={index}>
                  <td>
                    <Link to={`/jobs/${match.job_id}`}>
                      {match.job_title}
                    </Link>
                  </td>
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
        </div>
      )}
    </div>
  );
}

export default MatchesList;