import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Dashboard from './components/Dashboard';
import JobsList from './components/JobsList';
import CandidatesList from './components/CandidatesList';
import JobDetails from './components/JobDetails';
import CandidateDetails from './components/CandidateDetails';
import Navbar from './components/Navbar';
import InitializeSystem from './components/InitializeSystem';
import MatchesList from './components/MatchesList';
import ResumeUpload from './components/ResumeUpload';

function App() {
  const [stats, setStats] = useState({
    jobs: 0,
    candidates: 0,
    matches: 0,
    shortlisted: 0,
    interviews: 0
  });

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/stats');
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <Router>
      <div className="app">
        <Navbar />
        <div className="container mt-4">
          <Routes>
            <Route path="/" element={<Dashboard stats={stats} refreshStats={fetchStats} />} />
            <Route path="/initialize" element={<InitializeSystem refreshStats={fetchStats} />} />
            <Route path="/jobs" element={<JobsList />} />
            <Route path="/jobs/:id" element={<JobDetails refreshStats={fetchStats} />} />
            <Route path="/candidates" element={<CandidatesList />} />
            <Route path="/candidates/:id" element={<CandidateDetails />} />
            <Route path="/matches" element={<MatchesList />} />
            <Route path="/resume-upload" element={<ResumeUpload />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
