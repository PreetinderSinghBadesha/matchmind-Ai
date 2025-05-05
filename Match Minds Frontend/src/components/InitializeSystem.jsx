import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function InitializeSystem({ refreshStats }) {
  const [initializing, setInitializing] = useState(false);
  const [message, setMessage] = useState(null);
  const navigate = useNavigate();

  const handleInitialize = async () => {
    try {
      setInitializing(true);
      setMessage({ type: 'info', text: 'Initializing system...' });

      const response = await fetch('http://localhost:5000/api/initialize', {
        method: 'POST'
      });

      const data = await response.json();
      
      if (data.success) {
        setMessage({ type: 'success', text: 'System initialized successfully!' });
        refreshStats();
        setTimeout(() => navigate('/'), 2000); // Redirect to dashboard after 2 seconds
      } else {
        setMessage({ type: 'danger', text: `Error: ${data.message}` });
      }
    } catch (error) {
      setMessage({ type: 'danger', text: `Error: ${error.message}` });
    } finally {
      setInitializing(false);
    }
  };

  return (
    <div className="initialize-system">
      <h1>Initialize Job Screening System</h1>
      <p className="lead">
        Set up the multi-agent system by loading job descriptions and parsing candidate CVs
      </p>

      {message && (
        <div className={`alert alert-${message.type}`} role="alert">
          {message.text}
        </div>
      )}

      <div className="card mt-4">
        <div className="card-header">System Initialization</div>
        <div className="card-body">
          <h5 className="card-title">Set Up Job Screening System</h5>
          <p className="card-text">
            This will perform the following operations:
          </p>
          <ul>
            <li>Initialize the SQLite database for long-term memory</li>
            <li>Load job descriptions from the dataset</li>
            <li>Parse candidate CVs and extract key information</li>
          </ul>
          <div className="alert alert-warning">
            <strong>Note:</strong> Initializing the system will reset all current data.
            Only do this if you're setting up for the first time or want to start fresh.
          </div>
          <button
            className="btn btn-primary"
            onClick={handleInitialize}
            disabled={initializing}
          >
            {initializing ? 'Initializing...' : 'Initialize System'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default InitializeSystem;