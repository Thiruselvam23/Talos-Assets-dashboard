import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import Navbar from "../components/Navbar";
import { CHART_CONFIG, fetchChartData, fetchCascadingFilters, fetchHealth } from "../api/index";
import "./ChartPage.css";

// ── Custom Tooltip ────────────────────────────────────────────────────────────
function CustomTooltip({ active, payload, label, yLabel }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="custom-tooltip">
      <p className="tooltip-date">{label}</p>
      <p className="tooltip-value">
        {yLabel}: <span>{Number(payload[0].value).toLocaleString()}</span>
      </p>
    </div>
  );
}

// ── Filter Dropdown ───────────────────────────────────────────────────────────
function FilterDropdown({ label, options, value, onChange }) {
  return (
    <div className="filter-group">
      <label className="filter-label">{label}</label>
      <select
        className="filter-select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">All</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </select>
    </div>
  );
}

function formatYAxis(value) {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(0)}K`;
  return value;
}

// ── Bar label — full number, vertical ────────────────────────────────────────
function BarLabel({ x, y, width, value }) {
  if (!value && value !== 0) return null;
  return (
    <text
      x={x + width / 2}
      y={y - 6}
      fill="#8da5be"
      fontSize={11}
      fontFamily="monospace"
      textAnchor="start"
      transform={`rotate(-90, ${x + width / 2}, ${y - 6})`}
    >
      {Number(value).toLocaleString("en-IN", { useGrouping: false })}
    </text>
  );
}

// ── Main ChartPage ────────────────────────────────────────────────────────────
export default function ChartPage() {
  const { chartId } = useParams();
  const navigate = useNavigate();
  const config = CHART_CONFIG[chartId];

  const isBranch = config?.filterType === "branch";
  const sheet = isBranch ? "branch" : "lang";

  const [chartData, setChartData] = useState([]);
  const [filterOpts, setFilterOpts] = useState({ branch: [], dialer: [], language: [], agentname: [] });
  const [filters, setFilters] = useState({ branch: "", dialer: "", language: "", agentname: "" });
  const [chartTitle, setChartTitle] = useState("");
  const [dateRange, setDateRange] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeBar, setActiveBar] = useState(null);

  // Fetch date range from backend on mount
  useEffect(() => {
    fetchHealth().then((data) => {
      if (data?.date_range) {
        const fmt = (d) => d.split("-").reverse().join("-");
        setDateRange(`${fmt(data.date_range.from)} to ${fmt(data.date_range.to)}`);
      }
    }).catch(() => { });
  }, []);

  // ── Load cascading filter options whenever filters change ─────────────────
  useEffect(() => {
    fetchCascadingFilters(sheet, filters)
      .then(setFilterOpts)
      .catch(() => { });
  }, [sheet, filters.branch, filters.dialer, filters.language]);
  // agentname excluded — selecting an agent doesn't further restrict other filters

  // ── When a filter changes, reset downstream filters ───────────────────────
  const handleBranchChange = (v) => {
    // Resetting branch clears dialer/language and agent
    setFilters({ branch: v, dialer: "", language: "", agentname: "" });
  };

  const handleDialerChange = (v) => {
    // Resetting dialer clears agent only
    setFilters((f) => ({ ...f, dialer: v, agentname: "" }));
  };

  const handleLanguageChange = (v) => {
    setFilters((f) => ({ ...f, language: v, agentname: "" }));
  };

  const handleAgentChange = (v) => {
    setFilters((f) => ({ ...f, agentname: v }));
  };

  // ── Load chart data whenever filters change ───────────────────────────────
  const loadData = useCallback(async () => {
    if (!config) return;
    setLoading(true);
    setError(null);
    try {
      const activeFilters = isBranch
        ? { branch: filters.branch, dialer: filters.dialer, agentname: filters.agentname }
        : { branch: filters.branch, language: filters.language, agentname: filters.agentname };

      const res = await fetchChartData(config.endpoint, activeFilters);
      setChartData(res.data || []);
      setChartTitle(res.title || "");
    } catch {
      setError("No data available for the selected filters. Please modify the filter criteria and try again.");
    } finally {
      setLoading(false);
    }
  }, [config, filters, isBranch]);

  useEffect(() => { loadData(); }, [loadData]);

  const resetFilters = () => {
    setFilters({ branch: "", dialer: "", language: "", agentname: "" });
  };

  if (!config) {
    return (
      <div className="chart-page">
        <Navbar />
        <div className="chart-error">Chart not found.</div>
      </div>
    );
  }

  return (
    <div className="chart-page">
      <Navbar />

      {/* Go Back — top right */}
      <div className="chart-topbar">
        <button className="back-btn" onClick={() => navigate("/")}>
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path d="M10 3L5 8l5 5" stroke="currentColor" strokeWidth="2"
              strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Go Back
        </button>
      </div>

      <div className="chart-layout">

        {/* ── Sidebar ── */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <h2 className="sidebar-title">Filters</h2>
          </div>

          <div className="filter-section">
            {/* Branch — always shown, always all options */}
            <FilterDropdown
              label="branch"
              options={filterOpts.branch || []}
              value={filters.branch}
              onChange={handleBranchChange}
            />

            {/* Dialer (branchwise) OR Language (languagewise) */}
            {isBranch ? (
              <FilterDropdown
                label="dialer"
                options={filterOpts.dialer || []}
                value={filters.dialer}
                onChange={handleDialerChange}
              />
            ) : (
              <FilterDropdown
                label="language"
                options={filterOpts.language || []}
                value={filters.language}
                onChange={handleLanguageChange}
              />
            )}

            {/* Agent — always last, options depend on branch + dialer/language */}
            <FilterDropdown
              label="agentname"
              options={filterOpts.agentname || []}
              value={filters.agentname}
              onChange={handleAgentChange}
            />
          </div>

          <button className="reset-btn" onClick={resetFilters}>
            Reset Filters
          </button>
        </aside>

        {/* ── Chart area ── */}
        <main className="chart-main">

          {/* Banner */}
          <div className="chart-banner">
            <h1 className="chart-banner-title">
              {config.title}&nbsp;
              <span className="chart-date-range">{dateRange}</span>
            </h1>
          </div>

          {/* Chart card */}
          <div className="chart-card">
            <p className="chart-subtitle">{chartTitle}</p>

            {loading && (
              <div className="chart-loader">
                <div className="loader-spinner" />
                <span>Loading data…</span>
              </div>
            )}

            {error && (
              <div className="chart-error-block">
                <div className="chart-error-icon">⚠</div>
                <p className="chart-error-title">No Data Found</p>
                <p className="chart-error-msg">{error}</p>
              </div>
            )}

            {!loading && !error && chartData.length > 0 && (
              <ResponsiveContainer width="100%" height={420}>
                <BarChart
                  data={chartData}
                  margin={{ top: 100, right: 20, left: 8, bottom: 60 }}
                  barCategoryGap="28%"
                  onMouseLeave={() => setActiveBar(null)}
                >
                  <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(d) => d?.slice(5) ?? d}
                    tick={{ fill: "#8da5be", fontSize: 10, fontFamily: "monospace" }}
                    tickLine={false}
                    axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
                    angle={-45}
                    textAnchor="end"
                    interval={0}
                    height={60}
                  />
                  <YAxis
                    tickFormatter={formatYAxis}
                    tick={{ fill: "#8da5be", fontSize: 11, fontFamily: "monospace" }}
                    tickLine={false}
                    axisLine={false}
                    width={56}
                    label={{
                      value: config.yLabel,
                      angle: -90,
                      position: "insideLeft",
                      offset: -4,
                      style: { fill: "#8da5be", fontSize: 11 },
                    }}
                  />
                  <Tooltip
                    content={<CustomTooltip yLabel={config.yLabel} />}
                    cursor={{ fill: "rgba(255,255,255,0.04)" }}
                  />
                  <Bar
                    dataKey={config.metricKey}
                    radius={[4, 4, 0, 0]}
                    maxBarSize={30}
                    onMouseEnter={(_, index) => setActiveBar(index)}
                    label={<BarLabel />}
                  >
                    {chartData.map((_, index) => (
                      <Cell
                        key={index}
                        fill={activeBar === index ? "#4a9eff" : "#2d7dd2"}
                        opacity={activeBar === null || activeBar === index ? 1 : 0.6}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}

            {!loading && !error && chartData.length === 0 && (
              <div className="chart-empty">No data for the selected filters.</div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}