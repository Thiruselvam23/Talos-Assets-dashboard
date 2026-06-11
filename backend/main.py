"""
main.py
=======
5 chart endpoints — daily bar charts for the sales dashboard.

BRANCHWISE  — filters: branch, dialer, agentname (teamname)
  GET /charts/branch/call-count
  GET /charts/branch/talk-time

LANGUAGEWISE — filters: branch, language, agentname (teamname)
  GET /charts/lang/call-count
  GET /charts/lang/talk-time
  GET /charts/lang/connected-count

CASCADING FILTERS
  GET /filters   — returns available filter options based on current selections

Run:
    uvicorn main:app --reload --port 8000
Docs:
    http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from data_loader import load_raw_data, safe_records
from auth import router as auth_router

# ──────────────────────────────────────────────────────────────────────────────
# STARTUP — load once, cache in memory
# ──────────────────────────────────────────────────────────────────────────────

_cache: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    _cache.update(load_raw_data())
    yield
    _cache.clear()


app = FastAPI(
    title="Sales Dashboard Chart API",
    description="5 daily bar chart endpoints — branchwise and languagewise.",
    version="4.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://talos-assets-dashboard-1.onrender.com",
        "https://talos-assets-dashboard.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
app.include_router(auth_router)


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _get_branch() -> pd.DataFrame:
    if not _cache:
        raise HTTPException(503, "Data not loaded yet.")
    return _cache["raw_branch"].copy()


def _get_lang() -> pd.DataFrame:
    if not _cache:
        raise HTTPException(503, "Data not loaded yet.")
    return _cache["raw_lang"].copy()


def _apply_branch_filters(df, branch, dialer, agentname):
    if branch:
        df = df[df["branch"].str.lower() == branch.lower()]
    if dialer:
        df = df[df["dialer"].str.lower() == dialer.lower()]
    if agentname:
        df = df[df["agentname"].str.lower() == agentname.lower()]
    return df


def _apply_lang_filters(df, branch, language, agentname):
    if branch:
        df = df[df["branch"].str.lower() == branch.lower()]
    if language:
        df = df[df["language"].str.lower() == language.lower()]
    if agentname:
        df = df[df["agentname"].str.lower() == agentname.lower()]
    return df


def _label(value):
    return value if value else "(All)"


def _check_empty(df, filters):
    if df.empty:
        active = {k: v for k, v in filters.items() if v}
        raise HTTPException(404, f"No data found for filters: {active}")


def _group_by_date(df, metric_col, agg="sum"):
    result = (
        df.groupby("date_str")
        .agg(**{metric_col: (metric_col, agg)})
        .reset_index()
        .sort_values("date_str")
        .rename(columns={"date_str": "date"})
    )
    return result


# ──────────────────────────────────────────────────────────────────────────────
# CHART 1 — Branchwise Call Count
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/charts/branch/call-count", tags=["Branchwise"])
def branch_call_count(
    branch   : Optional[str] = Query(None),
    dialer   : Optional[str] = Query(None),
    agentname: Optional[str] = Query(None, description="Teamname e.g. Kp Sales Coimbatore"),
):
    df = _apply_branch_filters(_get_branch(), branch, dialer, agentname)
    _check_empty(df, {"branch": branch, "dialer": dialer, "agentname": agentname})
    result = _group_by_date(df, "call_count")
    result["call_count"] = result["call_count"].astype(int)
    return {
        "title": f"Branch: {_label(branch)} | Dialer: {_label(dialer)} | Team: {_label(agentname)}",
        "data" : safe_records(result),
    }


# ──────────────────────────────────────────────────────────────────────────────
# CHART 2 — Branchwise Talk Time
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/charts/branch/talk-time", tags=["Branchwise"])
def branch_talk_time(
    branch   : Optional[str] = Query(None),
    dialer   : Optional[str] = Query(None),
    agentname: Optional[str] = Query(None),
):
    df = _apply_branch_filters(_get_branch(), branch, dialer, agentname)
    _check_empty(df, {"branch": branch, "dialer": dialer, "agentname": agentname})
    result = _group_by_date(df, "total_talktime")
    result["total_talktime"] = result["total_talktime"].round(2)
    return {
        "title": f"Branch: {_label(branch)} | Dialer: {_label(dialer)} | Team: {_label(agentname)}",
        "data" : safe_records(result),
    }


# ──────────────────────────────────────────────────────────────────────────────
# CHART 3 — Languagewise Call Count
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/charts/lang/call-count", tags=["Languagewise"])
def lang_call_count(
    branch   : Optional[str] = Query(None),
    language : Optional[str] = Query(None),
    agentname: Optional[str] = Query(None),
):
    df = _apply_lang_filters(_get_lang(), branch, language, agentname)
    _check_empty(df, {"branch": branch, "language": language, "agentname": agentname})
    result = _group_by_date(df, "call_count")
    result["call_count"] = result["call_count"].astype(int)
    return {
        "title": f"Branch: {_label(branch)} | Language: {_label(language)} | Team: {_label(agentname)}",
        "data" : safe_records(result),
    }


# ──────────────────────────────────────────────────────────────────────────────
# CHART 4 — Languagewise Talk Time
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/charts/lang/talk-time", tags=["Languagewise"])
def lang_talk_time(
    branch   : Optional[str] = Query(None),
    language : Optional[str] = Query(None),
    agentname: Optional[str] = Query(None),
):
    df = _apply_lang_filters(_get_lang(), branch, language, agentname)
    _check_empty(df, {"branch": branch, "language": language, "agentname": agentname})
    result = _group_by_date(df, "total_talktime")
    result["total_talktime"] = result["total_talktime"].round(2)
    return {
        "title": f"Branch: {_label(branch)} | Language: {_label(language)} | Team: {_label(agentname)}",
        "data" : safe_records(result),
    }


# ──────────────────────────────────────────────────────────────────────────────
# CHART 5 — Languagewise Connected Call Count
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/charts/lang/connected-count", tags=["Languagewise"])
def lang_connected_count(
    branch   : Optional[str] = Query(None),
    language : Optional[str] = Query(None),
    agentname: Optional[str] = Query(None),
):
    df = _apply_lang_filters(_get_lang(), branch, language, agentname)
    _check_empty(df, {"branch": branch, "language": language, "agentname": agentname})
    result = _group_by_date(df, "connected_call_count")
    result["connected_call_count"] = result["connected_call_count"].astype(int)
    return {
        "title": f"Branch: {_label(branch)} | Language: {_label(language)} | Team: {_label(agentname)}",
        "data" : safe_records(result),
    }


# ──────────────────────────────────────────────────────────────────────────────
# CASCADING FILTERS
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/filters", tags=["Filters"])
def get_filters(
    sheet    : str           = Query("branch"),
    branch   : Optional[str] = Query(None),
    dialer   : Optional[str] = Query(None),
    language : Optional[str] = Query(None),
    agentname: Optional[str] = Query(None),
):
    if sheet == "branch":
        df = _get_branch()
        branches = sorted(df["branch"].unique().tolist())

        d = df.copy()
        if branch:
            d = d[d["branch"].str.lower() == branch.lower()]
        dialers = sorted(d["dialer"].unique().tolist())

        a = df.copy()
        if branch:
            a = a[a["branch"].str.lower() == branch.lower()]
        if dialer:
            a = a[a["dialer"].str.lower() == dialer.lower()]
        agents = sorted(a["agentname"].unique().tolist())

        return {"branch": branches, "dialer": dialers, "agentname": agents}

    else:
        df = _get_lang()
        branches = sorted(df["branch"].unique().tolist())

        l = df.copy()
        if branch:
            l = l[l["branch"].str.lower() == branch.lower()]
        languages = sorted(l["language"].unique().tolist())

        a = df.copy()
        if branch:
            a = a[a["branch"].str.lower() == branch.lower()]
        if language:
            a = a[a["language"].str.lower() == language.lower()]
        agents = sorted(a["agentname"].unique().tolist())

        return {"branch": branches, "language": languages, "agentname": agents}


# ──────────────────────────────────────────────────────────────────────────────
# HEALTH CHECK
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health():
    if not _cache:
        return {"status": "loading"}

    b = _cache["raw_branch"]
    l = _cache["raw_lang"]

    return {
        "status"    : "ok",
        "date_range": {
            "from": b["date_str"].min(),
            "to"  : b["date_str"].max(),
        },
        "filter_values": {
            "branch"   : sorted(b["branch"].unique().tolist()),
            "dialer"   : sorted(b["dialer"].unique().tolist()),
            "agentname": sorted(b["agentname"].unique().tolist()),
            "language" : sorted(l["language"].unique().tolist()),
        },
    }