import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function CandidatesList() {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/candidates');
        const data = await response.json();
        
        if (data.success) {
          setCandidates(data.candidates);
        } else {
          setError(data.message || 'Failed to fetch candidates');
        }
      } catch (error) {
        setError('Error connecting to server');
        console.error('Error fetching candidates:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCandidates();
  }, []);

  const filteredCandidates = candidates.filter(candidate => {
    const searchText = searchTerm.toLowerCase();
    return (
      candidate.name.toLowerCase().includes(searchText) ||
      (candidate.skills && candidate.skills.some(skill => skill.toLowerCase().includes(searchText)))
    );
  });

  if (loading) {
    return <div className="d-flex justify-content-center mt-5"><div className="spinner-border" role="status"></div></div>;
  }

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  return (
    <div className="candidates-list">
      <h1>Candidates</h1>
      <p className="lead">Browse available candidates processed by the AI system</p>
      
      <div className="mb-4">
        <input 
          type="text" 
          className="form-control" 
          placeholder="Search by name or skill..." 
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      
      {candidates.length === 0 ? (
        <div className="alert alert-info">
          No candidates found. Please initialize the system first.
        </div>
      ) : filteredCandidates.length === 0 ? (
        <div className="alert alert-info">
          No candidates match your search criteria.
        </div>
      ) : (
        <div className="row">
          {filteredCandidates.map((candidate) => (
            <div className="col-md-6 mb-4" key={candidate.id}>
              <div className="card h-100">
                <div className="card-header d-flex justify-content-between align-items-center">
                  <span>{candidate.name}</span>
                  <small>{candidate.email}</small>
                </div>
                <div className="card-body">
                  <h6>Skills:</h6>
                  <div className="mb-3">
                    {candidate.skills.slice(0, 7).map((skill, index) => (
                      <span key={index} className="badge bg-info me-2 mb-2">
                        {skill}
                      </span>
                    ))}
                    {candidate.skills.length > 7 && (
                      <span className="badge bg-secondary me-2 mb-2">
                        +{candidate.skills.length - 7} more
                      </span>
                    )}
                  </div>
                  
                  <div className="mb-3">
                    <h6>Experience: {candidate.experience.length > 0 ? `${candidate.experience.length} positions` : 'Not specified'}</h6>
                    <h6>Education: {candidate.education.length > 0 ? `${candidate.education.length} qualifications` : 'Not specified'}</h6>
                  </div>
                  
                  <Link to={`/candidates/${candidate.id}`} className="btn btn-primary">
                    View Profile
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default CandidatesList;