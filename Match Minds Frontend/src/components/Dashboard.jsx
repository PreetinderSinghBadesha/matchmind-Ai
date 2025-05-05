import { useState } from 'react';
import { Link } from 'react-router-dom';

function Dashboard({ stats, refreshStats }) {
  const [threshold, setThreshold] = useState(0.75);
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState(null);

  const handleProcessJobs = async () => {
    try {
      setProcessing(true);
      setMessage({ type: 'info', text: 'Processing jobs...' });

      const response = await fetch('http://localhost:5000/api/process-jobs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ threshold }),
      });

      const data = await response.json();
      
      if (data.success) {
        setMessage({ type: 'success', text: 'Jobs processed successfully!' });
        refreshStats();
      } else {
        setMessage({ type: 'danger', text: `Error: ${data.message}` });
      }
    } catch (error) {
      setMessage({ type: 'danger', text: `Error: ${error.message}` });
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="mb-1">Job Screening Dashboard</h1>
          <p className="lead text-muted">
            <i className="fas fa-robot me-2"></i>
            Multi-agent AI system for automated job screening and candidate matching
          </p>
        </div>
        <button 
          className="btn btn-primary d-none d-md-block" 
          onClick={refreshStats}
          
        >
          <i className="fas fa-sync-alt me-2"></i>
          Refresh Stats
        </button>
      </div>

      {message && (
        <div className={`alert alert-${message.type} d-flex align-items-center`} role="alert">
          <i className={`fas fa-${message.type === 'success' ? 'check-circle' : message.type === 'info' ? 'info-circle' : 'exclamation-triangle'} me-2`}></i>
          {message.text}
        </div>
      )}

      <div className="row mt-4">
        <div className="col-md-4">
          <div className="card mb-3">
            <div className="card-body text-center">
              <div className="icon-wrapper mb-3">
                <i className="fas fa-briefcase fa-3x text-primary"></i>
              </div>
              <h5 className="card-title">Jobs</h5>
              <p className="card-text display-4">{stats.jobs}</p>
              <Link to="/jobs" className="btn btn-primary">
                <i className="fas fa-search me-2"></i>
                View All Jobs
              </Link>
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card mb-3">
            <div className="card-body text-center">
              <div className="icon-wrapper mb-3">
                <i className="fas fa-user-tie fa-3x text-primary"></i>
              </div>
              <h5 className="card-title">Candidates</h5>
              <p className="card-text display-4">{stats.candidates}</p>
              <Link to="/candidates" className="btn btn-primary">
                <i className="fas fa-search me-2"></i>
                View All Candidates
              </Link>
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <div className="card mb-3">
            <div className="card-body text-center">
              <div className="icon-wrapper mb-3">
                <i className="fas fa-handshake fa-3x text-primary"></i>
              </div>
              <h5 className="card-title">Matches</h5>
              <p className="card-text display-4">{stats.matches}</p>
              <Link to="/matches" className="btn btn-primary">
                <i className="fas fa-search me-2"></i>
                View All Matches
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="row mt-2">
        <div className="col-md-6">
          <div className="card mb-3">
            <div className="card-body d-flex align-items-center">
              <div className="icon-container me-3">
                <i className="fas fa-check-circle fa-3x text-warning"></i>
              </div>
              <div>
                <h5 className="card-title">Shortlisted Candidates</h5>
                <p className="card-text display-4">{stats.shortlisted}</p>
                <div className="progress" style={{ height: '8px' }}>
                  <div 
                    className="progress-bar bg-warning" 
                    role="progressbar" 
                    style={{ width: `${stats.candidates ? (stats.shortlisted / stats.candidates) * 100 : 0}%` }}
                    aria-valuenow={stats.shortlisted} 
                    aria-valuemin="0" 
                    aria-valuemax={stats.candidates}
                  ></div>
                </div>
                <small className="text-muted">
                  {stats.candidates ? ((stats.shortlisted / stats.candidates) * 100).toFixed(1) : 0}% of total candidates
                </small>
              </div>
            </div>
          </div>
        </div>
        
        <div className="col-md-6">
          <div className="card mb-3">
            <div className="card-body d-flex align-items-center">
              <div className="icon-container me-3">
                <i className="fas fa-calendar-check fa-3x text-success"></i>
              </div>
              <div>
                <h5 className="card-title">Interviews Scheduled</h5>
                <p className="card-text display-4">{stats.interviews}</p>
                <div className="progress" style={{ height: '8px' }}>
                  <div 
                    className="progress-bar bg-success" 
                    role="progressbar" 
                    style={{ width: `${stats.shortlisted ? (stats.interviews / stats.shortlisted) * 100 : 0}%` }}
                    aria-valuenow={stats.interviews} 
                    aria-valuemin="0" 
                    aria-valuemax={stats.shortlisted}
                  ></div>
                </div>
                <small className="text-muted">
                  {stats.shortlisted ? ((stats.interviews / stats.shortlisted) * 100).toFixed(1) : 0}% of shortlisted candidates
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card mt-4">
        <div className="card-header bg-primary text-white d-flex align-items-center">
          <i className="fas fa-cogs me-2"></i>
          <span>Process Jobs</span>
        </div>
        <div className="card-body">
          <h5 className="card-title">Run Match Algorithm</h5>
          <p className="card-text">
            Process all jobs and candidates to find the best matches. Set the
            threshold (0.0-1.0) for shortlisting candidates.
          </p>
          <div className="mb-3">
            <label htmlFor="thresholdRange" className="form-label d-flex justify-content-between">
              <span>Match Threshold</span>
              <span className="badge bg-primary">{threshold}</span>
            </label>
            <div className="d-flex align-items-center">
              <span className="me-2">0.0</span>
              <input
                type="range"
                className="form-range flex-grow-1"
                min="0"
                max="1"
                step="0.05"
                id="thresholdRange"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
              />
              <span className="ms-2">1.0</span>
            </div>
            <div className="threshold-labels d-flex justify-content-between text-muted mt-1">
              <small>Low Selectivity</small>
              <small>High Selectivity</small>
            </div>
          </div>
          <button
            className="btn btn-success"
            onClick={handleProcessJobs}
            disabled={processing}
          >
            {processing ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Processing...
              </>
            ) : (
              <>
                <i className="fas fa-play me-2"></i>
                Process Jobs
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;