# Talos Assets — Sales Call Centre Dashboard

A full-stack web dashboard for visualising call centre performance data. Built with **FastAPI** (Python backend) and **React + Vite** (frontend). Data is read from an Excel file and displayed as interactive daily bar charts with cascading filters.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Set up Python virtual environment](#2-set-up-python-virtual-environment)
  - [3. Install backend dependencies](#3-install-backend-dependencies)
  - [4. Place the Excel file](#4-place-the-excel-file)
  - [5. Start the backend](#5-start-the-backend)
  - [6. Install frontend dependencies](#6-install-frontend-dependencies)
  - [7. Configure frontend environment](#7-configure-frontend-environment)
  - [8. Start the frontend](#8-start-the-frontend)
- [Switching to Database Mode](#switching-to-database-mode)
  - [SSH Tunnel Setup (local dev)](#ssh-tunnel-setup-local-dev)
  - [Direct Connection (production server)](#direct-connection-production-server)
- [Production Deployment](#production-deployment)
- [API Endpoints](#api-endpoints)
- [Charts and Filters](#charts-and-filters)
- [Data Pipeline](#data-pipeline)
- [Troubleshooting](#troubleshooting)

---

## Project Structure

```
Dashboard_project/
├── backend/
│   ├── data_loader.py       # Data pipeline — Excel or DB, ingest → clean → transform
│   ├── main.py              # FastAPI app — all chart and filter endpoints
│   ├── auth.py              # User auth endpoints (optional, not used in no-login mode)
│   ├── models.py            # Pydantic response schemas
│   ├── users.json           # User accounts (admin + non-admin)
│   └── .env                 # DB credentials if using database mode (never commit)
├── frontend/
│   ├── public/
│   │   └── logo.png         # Company logo (navbar + favicon)
│   └── src/
│       ├── api/
│       │   └── index.js     # All Axios API calls centralised here
│       ├── components/
│       │   ├── DataCard.jsx / .css      # Clickable home page cards
│       │   └── Navbar.jsx / .css        # Top navigation bar with logo
│       ├── pages/
│       │   ├── Home.jsx / .css          # Dashboard home — branchwise + languagewise
│       │   └── ChartPage.jsx / .css     # Chart page with bar chart and filters
│       ├── App.jsx                      # Route definitions
│       ├── main.jsx                     # React entry point
│       └── index.css                    # Global styles and design tokens
│   └── .env                             # Frontend env vars (API URL)
├── data/
│   └── branch_lang_report_YYYY-MM-DD.xlsx   # Excel data source
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Recharts, Axios, React Router |
| Backend | Python 3.11+, FastAPI, Uvicorn, Pandas, Openpyxl |
| Database (optional) | PostgreSQL via Psycopg2 |
| Production server | Nginx + systemd |

---

## Prerequisites

Install the following before starting:

- **Python 3.11+** — https://www.python.org/downloads/
- **Node.js 20+** — https://nodejs.org/
- **Git** — https://git-scm.com/
- **VS Code** (recommended) — https://code.visualstudio.com/

---

## Local Development Setup

### 1. Clone the repository

```powershell
git clone <your-repo-url>
cd Dashboard_project
```

### 2. Set up Python virtual environment

```powershell
python -m venv venv
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of your terminal line.

### 3. Install backend dependencies

```powershell
cd backend
pip install fastapi uvicorn pandas openpyxl numpy python-dotenv python-jose passlib
pip freeze > requirements.txt
```

### 4. Place the Excel file

Put your Excel file in the `data/` folder:

```
Dashboard_project/
└── data/
    └── branch_lang_report_2026-05-13.xlsx
```

The Excel file must have exactly **two sheets**:

**Sheet 1 — "Branchwise data"**

| Column | Type | Description |
|---|---|---|
| calldate | date | Date of the calls |
| branch | string | Branch name |
| dialer | string | Dialer system used |
| teamname | string | Agent team name |
| call_count | integer | Number of calls |
| total_talktime | float | Total talk time in seconds |

**Sheet 2 — "Languagewise data"**

| Column | Type | Description |
|---|---|---|
| calldate | date | Date of the calls |
| branch | string | Branch name |
| language | string | Language of the calls |
| teamname | string | Agent team name |
| call_count | integer | Number of calls |
| total_talktime | float | Total talk time in seconds |
| connected_call_count | integer | Number of connected calls |

> **To use a different filename:** Open `backend/data_loader.py` and update the `EXCEL_PATH` variable at the top of the file.

### 5. Start the backend

```powershell
cd backend
uvicorn main:app --reload --port 8000
```

Expected output:
```
[ingest] Branchwise   : shape=(1044, 6) ...
[ingest] Languagewise : shape=(859, 7) ...
[ready] Excel data loaded.
INFO: Uvicorn running on http://127.0.0.1:8000
```

Verify at: `http://localhost:8000/health`

### 6. Install frontend dependencies

Open a **new** PowerShell terminal:

```powershell
cd frontend
npm install
```

### 7. Configure frontend environment

Create or update `frontend/.env`:

```dotenv
VITE_API_URL=http://localhost:8000
```

### 8. Start the frontend

```powershell
cd frontend
npm run dev
```

Open your browser at: `http://localhost:5173`

The dashboard home page loads immediately — no login required.

---

## Switching to Database Mode

To switch from Excel to a live PostgreSQL database, replace `backend/data_loader.py` with the database version.

### SSH Tunnel Setup (local dev)

When the database is on AWS RDS and not publicly accessible, you need an SSH tunnel running in a separate terminal before starting the backend.

**Fix key file permissions (run once):**
```powershell
icacls "C:\path\to\datanalyst-kalyan-livedb" /inheritance:r /grant:r "$($env:USERNAME):(R)"
```

**Open the tunnel (keep this terminal open):**
```powershell
ssh -i "C:\path\to\datanalyst-kalyan-livedb" `
    -L 5933:your-rds-host.rds.amazonaws.com:5933 `
    datanalyst@BASTION_IP -N
```

**Update `backend/.env`:**
```dotenv
DB_HOST=localhost
DB_PORT=5933
DB_NAME=your_database_name
DB_USER=your_db_username
DB_PASSWORD=your_db_password
```

### Direct Connection (production server)

When the backend is deployed on a server with direct DB access, no tunnel is needed.

**Update `backend/.env`:**
```dotenv
DB_HOST=your_actual_db_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_db_username
DB_PASSWORD=your_db_password
```

---

## Production Deployment

### 1. Update frontend .env

```dotenv
VITE_API_URL=http://YOUR_SERVER_IP:8000
```

### 2. Build the frontend

```powershell
cd frontend
npm run build
```

### 3. Upload to server

```powershell
scp -i "path/to/key.pem" -r backend ubuntu@YOUR_SERVER_IP:~/dashboard/
scp -i "path/to/key.pem" -r frontend/dist ubuntu@YOUR_SERVER_IP:~/dashboard/frontend_dist/
```

### 4. Install server dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx -y

cd ~/dashboard/backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pandas openpyxl numpy python-dotenv python-jose passlib
```

### 5. Run backend as a systemd service

```bash
sudo nano /etc/systemd/system/dashboard.service
```

Paste:
```ini
[Unit]
Description=Talos Assets Sales Dashboard API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/dashboard/backend
ExecStart=/home/ubuntu/dashboard/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start dashboard
sudo systemctl enable dashboard
sudo systemctl status dashboard
```

### 6. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/dashboard
```

Paste:
```nginx
server {
    listen 80;
    server_name YOUR_SERVER_IP;

    root /home/ubuntu/dashboard/frontend_dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo ufw allow 80 && sudo ufw allow 8000 && sudo ufw allow 22 && sudo ufw enable
```

Visit `http://YOUR_SERVER_IP` — the dashboard opens directly.

---

## API Endpoints

All endpoints available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server status + available filter values |
| `GET` | `/charts/branch/call-count` | Daily call count — branchwise |
| `GET` | `/charts/branch/talk-time` | Daily talk time — branchwise |
| `GET` | `/charts/lang/call-count` | Daily call count — languagewise |
| `GET` | `/charts/lang/talk-time` | Daily talk time — languagewise |
| `GET` | `/charts/lang/connected-count` | Daily connected call count — languagewise |
| `GET` | `/filters` | Cascading filter options based on selections |

All chart endpoints accept optional query parameters:

```
/charts/branch/call-count?branch=Chennai&dialer=Airtel&agentname=Sales+Executive+Chennai
/charts/lang/call-count?branch=Bangalore&language=Kannada&agentname=Key+Account+Kannada
```

---

## Charts and Filters

Five charts are available from the home page:

**Branchwise (2 charts):**
- Call Count per day — X axis: date, Y axis: total calls
- Talk Time per day — X axis: date, Y axis: total seconds

Filters: `branch`, `dialer`, `teamname`

**Languagewise (3 charts):**
- Call Count per day
- Talk Time per day
- Connected Call Count per day

Filters: `branch`, `language`, `teamname`

### Cascading Filters

Filters update each other automatically:

```
Branchwise:
  Select branch  →  Dialer options narrow  →  Team options narrow
  Select dialer  →  Team options narrow

Languagewise:
  Select branch   →  Language options narrow  →  Team options narrow
  Select language →  Team options narrow
```

This prevents selecting a combination that returns no data.

---

## Data Pipeline

Every time the server starts, the pipeline runs automatically:

```
Excel file (Branchwise + Languagewise sheets)
        ↓
    _ingest()        Read both sheets with openpyxl
        ↓
    _clean()         Fix types, strip strings, drop dupes, drop zero rows
        ↓
    _transform()     Add date_str, rename teamname → agentname
        ↓
    RAM cache        Stored in memory — no file I/O on each request
        ↓
    FastAPI endpoints   Filter rows → group by date → sum metric
        ↓
    React + Recharts    Bar chart rendered in browser
```

To update the data — replace the Excel file in `data/` and restart the backend server. The pipeline re-runs automatically on startup.

---

## Troubleshooting

**Excel file not found:**
```
FileNotFoundError: Excel file not found: .../data/branch_lang_report_2026-05-13.xlsx
```
→ Check the filename matches exactly in `data_loader.py`. Update `EXCEL_PATH` at the top of the file.

**Wrong sheet name:**
```
ValueError: Worksheet named 'Branchwise data' not found
```
→ Open the Excel file and check the exact sheet tab names. Update `SHEET_BRANCH` and `SHEET_LANG` in `data_loader.py`.

**`recharts` not found:**
```powershell
cd frontend && npm install recharts
```

**Frontend shows blank page:**
- Check browser console (F12) for errors
- Confirm `VITE_API_URL=http://localhost:8000` in `frontend/.env`
- Confirm backend is running and `http://localhost:8000/health` returns `"status": "ok"`

**CORS error in browser:**
- Make sure backend is running on port 8000
- Make sure `frontend/.env` has the correct `VITE_API_URL`

**Nginx 502 Bad Gateway on server:**
```bash
sudo systemctl status dashboard       # check backend is running
sudo journalctl -u dashboard -f       # view live backend logs
sudo systemctl restart dashboard      # restart backend
```

**Data not updating after replacing Excel file:**
- Restart the backend: `Ctrl+C` then `uvicorn main:app --reload --port 8000`
- The pipeline only runs on server startup

---

## Important Notes

- Never commit `backend/.env` or SSH key files to Git. Add to `.gitignore`:
  ```
  backend/.env
  frontend/.env
  data/datanalyst-kalyan-livedb
  data/*.xlsx
  ```
- The `data/*.xlsx` rule keeps sensitive Excel data out of the repository.
- To update data daily, replace the Excel file and restart the backend, or switch to database mode for automatic daily refresh.