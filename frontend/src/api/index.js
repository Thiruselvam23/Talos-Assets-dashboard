import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 10000,
});

// Chart config map — dateRange is fetched dynamically from /health
export const CHART_CONFIG = {
  "branch-call-count": {
    endpoint: "/charts/branch/call-count",
    title: "Call Count",
    pageTitle: "Branchwise Call Count",
    yLabel: "Call Count",
    metricKey: "call_count",
    filterType: "branch",
  },
  "branch-talk-time": {
    endpoint: "/charts/branch/talk-time",
    title: "Talk Time / Seconds",
    pageTitle: "Branchwise Talk Time",
    yLabel: "Talk Time (Seconds)",
    metricKey: "total_talktime",
    filterType: "branch",
  },
  "lang-call-count": {
    endpoint: "/charts/lang/call-count",
    title: "Call Count",
    pageTitle: "Languagewise Call Count",
    yLabel: "Call Count",
    metricKey: "call_count",
    filterType: "lang",
  },
  "lang-talk-time": {
    endpoint: "/charts/lang/talk-time",
    title: "Talk Time / Seconds",
    pageTitle: "Languagewise Talk Time",
    yLabel: "Talk Time (Seconds)",
    metricKey: "total_talktime",
    filterType: "lang",
  },
  "lang-connected-count": {
    endpoint: "/charts/lang/connected-count",
    title: "Connected Call Count",
    pageTitle: "Languagewise Connected Call Count",
    yLabel: "Connected Call Count",
    metricKey: "connected_call_count",
    filterType: "lang",
  },
};

// Fetch chart data with optional filters
export async function fetchChartData(endpoint, filters = {}) {
  const params = Object.fromEntries(
    Object.entries(filters).filter(([, v]) => v && v !== "")
  );
  const res = await api.get(endpoint, { params });
  return res.data;
}

// Fetch health — returns date_range and filter_values
export async function fetchHealth() {
  const res = await api.get("/health");
  return res.data;
}

// Fetch available filter values from /health
export async function fetchFilterValues() {
  const res = await api.get("/health");
  return res.data.filter_values;
}

// Fetch cascading filter options based on current selections
export async function fetchCascadingFilters(sheet, currentFilters = {}) {
  const params = { sheet };
  if (currentFilters.branch) params.branch = currentFilters.branch;
  if (currentFilters.dialer) params.dialer = currentFilters.dialer;
  if (currentFilters.language) params.language = currentFilters.language;
  if (currentFilters.agentname) params.agentname = currentFilters.agentname;
  const res = await api.get("/filters", { params });
  return res.data;
}