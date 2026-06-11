"""
models.py
=========
One Pydantic schema per chart.
Every chart returns a list of daily data points — one entry per call date.

Branchwise (2 charts):
  BranchDailyCallCount   → date + call_count
  BranchDailyTalkTime    → date + total_talktime

Languagewise (3 charts):
  LangDailyCallCount     → date + call_count
  LangDailyTalkTime      → date + total_talktime
  LangDailyConnected     → date + connected_call_count
"""

from pydantic import BaseModel


class BranchDailyCallCount(BaseModel):
    date        : str
    call_count  : int


class BranchDailyTalkTime(BaseModel):
    date            : str
    total_talktime  : float


class LangDailyCallCount(BaseModel):
    date        : str
    call_count  : int


class LangDailyTalkTime(BaseModel):
    date            : str
    total_talktime  : float


class LangDailyConnected(BaseModel):
    date                  : str
    connected_call_count  : int 