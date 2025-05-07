import { useState } from 'react';

function ResumeUpload() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [matchResults, setMatchResults] = useState(null);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setFileName(selectedFile.name);
      setError(null);
    } else {
      setFile(null);
      setFileName('');
      setError('Please select a PDF file');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    try {
      setUploading(true);
      setMessage({ type: 'info', text: 'Uploading and analyzing your resume...' });
      
      // Create form data for the file upload
      const formData = new FormData();
      formData.append('resume', file);

      // Upload the file to server
      const response = await fetch('http://localhost:5000/api/upload-resume', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      
      if (data.success) {
        setMessage({ type: 'success', text: 'Resume analyzed successfully!' });
        setMatchResults(data.matches);
      } else {
        setMessage({ type: 'danger', text: data.message || 'Error processing resume' });
      }
    } catch (error) {
      setMessage({ type: 'danger', text: `Error: ${error.message}` });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="resume-upload">
      <h1>Find Matching Jobs</h1>
      <p className="lead">Upload your resume to find matching job opportunities</p>

      {message && (
        <div className={`alert alert-${message.type}`} role="alert">
          {message.text}
        </div>
      )}

      <div className="card mb-4">
        <div className="card-header">
          <h4>Upload Resume</h4>
        </div>
        <div className="card-body">
          <div className="mb-3">
            <label htmlFor="resumeUpload" className="form-label">Resume (PDF format only)</label>
            <input 
              type="file" 
              className="form-control" 
              id="resumeUpload" 
              accept=".pdf" 
              onChange={handleFileChange}
            />
            {error && <div className="text-danger mt-2">{error}</div>}
            {fileName && <div className="text-muted mt-2">Selected file: {fileName}</div>}
          </div>
          <button 
            className="btn btn-primary" 
            onClick={handleUpload} 
            disabled={!file || uploading}
          >
            {uploading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Processing...
              </>
            ) : (
              'Find Matching Jobs'
            )}
          </button>
        </div>
      </div>

      {matchResults && (
        <div className="card">
          <div className="card-header">
            <h4>Job Matches</h4>
          </div>
          <div className="card-body">
            {matchResults.length === 0 ? (
              <div className="alert alert-info">No matching jobs found.</div>
            ) : (
              <>
                <p>We found {matchResults.length} potential job matches:</p>
                <div className="table-responsive">
                  <table className="table table-striped">
                    <thead>
                      <tr>
                        <th>Job Title</th>
                        <th>Match Score</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {matchResults.sort((a, b) => b.match_score - a.match_score).map((match) => (
                        <tr key={match.job_id}>
                          <td>{match.job_title}</td>
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
                            <a href={`/jobs/${match.job_id}`} className="btn btn-sm btn-primary">View Job</a>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ResumeUpload;