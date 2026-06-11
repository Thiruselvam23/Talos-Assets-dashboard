import { useNavigate } from "react-router-dom";
import "./DataCard.css";

export default function DataCard({ chartId, title, index }) {
  const navigate = useNavigate();

  return (
    <div
      className="data-card"
      style={{ animationDelay: `${index * 0.1}s` }}
      onClick={() => navigate(`/chart/${chartId}`)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === "Enter" && navigate(`/chart/${chartId}`)}
    >
      <div className="card-inner">
        <div className="card-accent-line" />
        <div className="card-content">
          <h3 className="card-title">{title}</h3>
        </div>
        <div className="card-arrow">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path
              d="M4 10h12M11 5l5 5-5 5"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      </div>
    </div>
  );
}