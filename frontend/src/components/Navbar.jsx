import { useNavigate } from "react-router-dom";
import "./Navbar.css";

export default function Navbar() {
  const navigate = useNavigate();

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        {/* Left spacer */}
        <div className="navbar-side" />

        {/* Centered logo — clicking returns to home */}
        <div
          className="navbar-logo"
          onClick={() => navigate("/")}
          style={{ cursor: "pointer" }}
          title="Go to Home"
        >
          <img
            src="/logo.png"
            alt="Talos Assets"
            className="logo-img"
            onError={(e) => {
              e.target.style.display = "none";
              e.target.nextSibling.style.display = "flex";
            }}
          />
          <span className="logo-fallback" style={{ display: "none" }}>
            <span className="logo-text">Talos Assets</span>
          </span>
        </div>

        {/* Right spacer */}
        <div className="navbar-side" />
      </div>
    </nav>
  );
}