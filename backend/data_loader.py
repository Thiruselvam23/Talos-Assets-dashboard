"""
data_loader.py
==============
Reads data from the Excel file instead of the database.
Source file: data/branch_lang_report_YYYY-MM-DD.xlsx

Sheets:
    "Branchwise data"   → calldate | branch | dialer | teamname | call_count | total_talktime
    "Languagewise data" → calldate | branch | language | teamname | call_count | total_talktime | connected_call_count

To switch back to database mode, replace this file with the DB version of data_loader.py.
"""

import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

# ── Configuration ─────────────────────────────────────────────────────────────
# Update this filename when a new Excel file arrives
EXCEL_PATH   = Path(__file__).parent.parent / "data" / "branch_lang_report_2026-05-13.xlsx"
SHEET_BRANCH = "Branchwise data"
SHEET_LANG   = "Languagewise data"


# ── Phase 1: Ingest ───────────────────────────────────────────────────────────

def _ingest(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not path.exists():
        raise FileNotFoundError(
            f"Excel file not found: {path}\n"
            f"Make sure the file is placed in the data/ folder."
        )

    branch_df = pd.read_excel(path, sheet_name=SHEET_BRANCH, engine="openpyxl")
    lang_df   = pd.read_excel(path, sheet_name=SHEET_LANG,   engine="openpyxl")

    print(f"[ingest] Branchwise   : shape={branch_df.shape}  cols={branch_df.columns.tolist()}")
    print(f"[ingest] Languagewise : shape={lang_df.shape}  cols={lang_df.columns.tolist()}")
    print(f"[ingest] Branchwise nulls  : {branch_df.isnull().sum().to_dict()}")
    print(f"[ingest] Languagewise nulls: {lang_df.isnull().sum().to_dict()}")

    return branch_df, lang_df


# ── Phase 2: Clean ────────────────────────────────────────────────────────────

def _clean_branch(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Dates
    df["calldate"] = pd.to_datetime(df["calldate"], errors="coerce")
    df = df.dropna(subset=["calldate"])

    # Numerics
    df["call_count"]     = pd.to_numeric(df["call_count"],     errors="coerce").fillna(0).astype(int)
    df["total_talktime"] = pd.to_numeric(df["total_talktime"], errors="coerce").fillna(0.0)

    # Strings
    for col in ["branch", "dialer", "teamname"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # Drop dupes and zero-call rows
    before = len(df)
    df = df.drop_duplicates()
    df = df[df["call_count"] >= 1]
    print(f"[clean:branch] removed {before - len(df)} rows  →  {len(df)} rows remain")

    # Add date string for groupby
    df["date_str"] = df["calldate"].dt.strftime("%Y-%m-%d")

    return df.reset_index(drop=True)


def _clean_lang(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Dates
    df["calldate"] = pd.to_datetime(df["calldate"], errors="coerce")
    df = df.dropna(subset=["calldate"])

    # Numerics
    df["call_count"]           = pd.to_numeric(df["call_count"],           errors="coerce").fillna(0).astype(int)
    df["total_talktime"]       = pd.to_numeric(df["total_talktime"],       errors="coerce").fillna(0.0)
    df["connected_call_count"] = pd.to_numeric(df["connected_call_count"], errors="coerce").fillna(0).astype(int)

    # Strings
    for col in ["branch", "language", "teamname"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # Drop dupes and zero-call rows
    before = len(df)
    df = df.drop_duplicates()
    df = df[df["call_count"] >= 1]
    print(f"[clean:lang]   removed {before - len(df)} rows  →  {len(df)} rows remain")

    # Add date string for groupby
    df["date_str"] = df["calldate"].dt.strftime("%Y-%m-%d")

    return df.reset_index(drop=True)


# ── Phase 3: Rename teamname → agentname ─────────────────────────────────────
# main.py and all endpoints use "agentname" as the filter column name.
# The Excel sheet uses "teamname". Rename here so nothing else needs to change.

def _transform_branch(df: pd.DataFrame) -> pd.DataFrame:
    if "teamname" in df.columns:
        df = df.rename(columns={"teamname": "agentname"})
    return df


def _transform_lang(df: pd.DataFrame) -> pd.DataFrame:
    if "teamname" in df.columns:
        df = df.rename(columns={"teamname": "agentname"})
    return df


# ── NaN-safe serialiser ───────────────────────────────────────────────────────

def _safe_record(row: dict) -> dict:
    out = {}
    for k, v in row.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            out[k] = None
        elif isinstance(v, np.integer):
            out[k] = int(v)
        elif isinstance(v, np.floating):
            out[k] = None if math.isnan(float(v)) else round(float(v), 4)
        elif isinstance(v, np.bool_):
            out[k] = bool(v)
        else:
            out[k] = v
    return out


def safe_records(df: pd.DataFrame) -> list[dict]:
    return [_safe_record(r) for r in df.to_dict(orient="records")]


# ── Public entry point ────────────────────────────────────────────────────────

def load_raw_data() -> dict:
    """
    Run the full pipeline and return two cleaned DataFrames.

    Returns:
        raw_branch : Branchwise DataFrame
                     cols: calldate | date_str | branch | dialer |
                           agentname | call_count | total_talktime
        raw_lang   : Languagewise DataFrame
                     cols: calldate | date_str | branch | language |
                           agentname | call_count | total_talktime |
                           connected_call_count
    """
    branch_raw, lang_raw = _ingest(EXCEL_PATH)

    branch = _transform_branch(_clean_branch(branch_raw))
    lang   = _transform_lang(_clean_lang(lang_raw))

    print(f"[ready] Excel data loaded.")
    print(f"        Branches  : {sorted(branch['branch'].unique().tolist())}")
    print(f"        Dialers   : {sorted(branch['dialer'].unique().tolist())}")
    print(f"        Agents    : {sorted(branch['agentname'].unique().tolist())}")
    print(f"        Languages : {sorted(lang['language'].unique().tolist())}")
    print(f"        Date range: {branch['date_str'].min()} → {branch['date_str'].max()}")

    return {"raw_branch": branch, "raw_lang": lang}


# ── Smoke test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    data = load_raw_data()

    print("\n=== BRANCH sample (5 rows) ===")
    print(data["raw_branch"].head().to_string())

    print("\n=== LANG sample (5 rows) ===")
    print(data["raw_lang"].head().to_string())