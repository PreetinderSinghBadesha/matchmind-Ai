import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function JobsList() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/jobs');
        const data = await response.json();
        
        if (data.success) {
          setJobs(data.jobs);
        } else {
          setError(data.message || 'Failed to fetch jobs');
        }
      } catch (error) {
        setError('Error connecting to server');
        console.error('Error fetching jobs:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, []);

  if (loading) {
    return <div className="d-flex justify-content-center mt-5"><div className="spinner-border" role="status"></div></div>;
  }

  if (error) {
    return <div className="alert alert-danger">{error}</div>;
  }

  return (
    <div className="jobs-list">
      <h1>Job Descriptions</h1>
      <p className="lead">Browse available job descriptions processed by the AI system</p>
      
      {jobs.length === 0 ? (
        <div className="alert alert-info">
          No jobs found. Please initialize the system first.
        </div>
      ) : (
        <div className="row">
          {jobs.map((job) => (
            <div className="col-md-6 mb-4" key={job.id}>
              <div className="card h-100">
                <div className="card-header">{job.title}</div>
                <div className="card-body">
                  <p className="card-text">
                    {job.summary || job.description.substring(0, 150) + '...'}
                  </p>
                  <h6>Required Skills:</h6>
                  <div className="mb-2">
                    {job.required_skills.slice(0, 5).map((skill, index) => (
                      <span key={index} className="badge bg-info me-2 mb-1">
                        {skill}
                      </span>
                    ))}
                    {job.required_skills.length > 5 && (
                      <span className="badge bg-secondary me-2 mb-1">
                        +{job.required_skills.length - 5} more
                      </span>
                    )}
                  </div>
                  <Link to={`/jobs/${job.id}`} className="btn btn-primary">
                    View Details
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

export default JobsList;