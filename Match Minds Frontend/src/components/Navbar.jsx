import { Link, useLocation } from 'react-router-dom';

function Navbar() {
  const location = useLocation();
  
  // Function to check if a link is active
  const isActive = (path) => location.pathname === path;
  
  return (
    <nav className="navbar navbar-expand-lg navbar-dark fixed-top">
      <div className="container">
        <Link className="navbar-brand" to="/">
          <i className="fas fa-brain me-2"></i>
          MatchMind AI
        </Link>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav">
            <li className="nav-item">
              <Link className={`nav-link ${isActive('/') ? 'active' : ''}`} to="/">
                <i className="fas fa-chart-bar me-1"></i> Dashboard
              </Link>
            </li>
            <li className="nav-item">
              <Link className={`nav-link ${isActive('/initialize') ? 'active' : ''}`} to="/initialize">
                <i className="fas fa-cogs me-1"></i> Initialize System
              </Link>
            </li>
            <li className="nav-item">
              <Link className={`nav-link ${isActive('/jobs') ? 'active' : ''}`} to="/jobs">
                <i className="fas fa-briefcase me-1"></i> Jobs
              </Link>
            </li>
            <li className="nav-item">
              <Link className={`nav-link ${isActive('/candidates') ? 'active' : ''}`} to="/candidates">
                <i className="fas fa-user-tie me-1"></i> Candidates
              </Link>
            </li>
            <li className="nav-item">
              <Link className={`nav-link ${isActive('/matches') ? 'active' : ''}`} to="/matches">
                <i className="fas fa-handshake me-1"></i> Matches
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;