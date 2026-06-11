import Navbar from "../components/Navbar";
import DataCard from "../components/DataCard";
import "./Home.css";

const BRANCH_CARDS = [
  { chartId: "branch-call-count", title: "Branchwise Call Count" },
  { chartId: "branch-talk-time", title: "Branchwise Talk Time" },
];

const LANG_CARDS = [
  { chartId: "lang-call-count", title: "Languagewise Call Count" },
  { chartId: "lang-talk-time", title: "Languagewise Talk Time" },
  { chartId: "lang-connected-count", title: "Languagewise Connected Call Count" },
];

export default function Home() {
  return (
    <div className="home-page">
      <Navbar />

      <main className="home-main">
        {/* Left panel — Branchwise */}
        <section className="panel panel-left">
          <div className="panel-header">
            <h2 className="panel-title">Branchwise Data</h2>
          </div>
          <div className="card-list">
            {BRANCH_CARDS.map((card, i) => (
              <DataCard key={card.chartId} {...card} index={i} />
            ))}
          </div>
        </section>

        {/* Divider */}
        <div className="panel-divider">
          <div className="divider-line" />
        </div>

        {/* Right panel — Languagewise */}
        <section className="panel panel-right">
          <div className="panel-header">
            <h2 className="panel-title">Languagewise Data</h2>
          </div>
          <div className="card-list">
            {LANG_CARDS.map((card, i) => (
              <DataCard key={card.chartId} {...card} index={i} />
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}