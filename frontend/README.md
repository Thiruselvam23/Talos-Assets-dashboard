# Marketsof1 Sales Dashboard

A full-stack web dashboard for visualising call centre performance data. Built with **FastAPI** (Python backend) and **React + Vite** (frontend). Data is fetched from a PostgreSQL database and displayed as interactive daily bar charts with cascading filters.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Set up the Python virtual environment](#2-set-up-the-python-virtual-environment)
  - [3. Install backend dependencies](#3-install-backend-dependencies)
  - [4. Configure backend environment variables](#4-configure-backend-environment-variables)
  - [5. Set up the SSH tunnel (local development only)](#5-set-up-the-ssh-tunnel-local-development-only)
  - [6. Test the database connection](#6-test-the-database-connection)
  - [7. Start the backend server](#7-start-the-backend-server)
  - [8. Install frontend dependencies](#8-install-frontend-dependencies)
  - [9. Configure frontend environment variables](#9-configure-frontend-environment-variables)
  - [10. Start the frontend](#10-start-the-frontend)
- [Production Deployment](#production-deployment)
  - [1. Update environment variables](#1-update-environment-variables)
  - [2. Build the frontend](#2-build-the-frontend)
  - [3. Upload to server](#3-upload-to-server)
  - [4. Install server dependencies](#4-install-server-dependencies)
  - [5. Run backend as a service](#5-run-backend-as-a-service)
  - [6. Configure Nginx](#6-configure-nginx)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Charts and Filters](#charts-and-filters)
- [User Management](#user-management)
- [Data Pipeline](#data-pipeline)
- [Troubleshooting](#troubleshooting)

---

## Project Structure

```
Dashboard_project/
├── backend/
│   ├── data_loader.py       # DB connection, data pipeline (ingest → clean → transform)
│   ├── main.py              # FastAPI app — all chart and filter endpoints
│   ├── auth.py              # Login, JWT tokens, user management endpoints
│   ├── models.py            # Pydantic response schemas
│   ├── users.json           # User store (admin + non-admin accounts)
│   └── .env                 # DB credentials (never commit this)
├── frontend/
│   ├── public/
│   │   └── logo1.png        # Company logo (favicon + navbar)
│   ├── src/
│   │   ├── api/
│   │   │   └── index.js     # All Axios API calls centralised here
│   │   ├── components/
│   │   │   ├── DataCard.jsx / .css      # Clickable home page cards
│   │   │   ├── Navbar.jsx / .css        # Top navigation bar
│   │   │   └── ProtectedRoute.jsx       # Auth guard for protected pages
│   │   ├── context/
│   │   │   └── AuthContext.jsx          # Global auth state (login/logout/token)
│   │   ├── pages/
│   │   │   ├── Login.jsx / .css         # Login page
│   │   │   ├── Home.jsx / .css          # Dashboard home (split branchwise/languagewise)
│   │   │   ├── ChartPage.jsx / .css     # Individual chart page with filters
│   │   │   └── AdminPage.jsx / .css     # User management (admin only)
│   │   ├── App.jsx                      # Route definitions
│   │   ├── main.jsx                     # React entry point
│   │   └── index.css                    # Global styles and design tokens
│   └── .env                             # Frontend env vars (API URL, login credentials)
├── data/
│   ├── datanalyst-kalyan-livedb         # SSH private key (local dev only, never commit)
│   └── branch_lang_report_*.xlsx        # Sample Excel file (fallback/testing)
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Recharts, Axios, React Router, Tailwind-compatible CSS |
| Backend | Python 3.11+, FastAPI, Uvicorn, Pandas, Psycopg2 |
| Auth | JWT tokens (python-jose), users.json store |
| Database | PostgreSQL (AWS RDS) |
| Local tunnel | SSH tunnel via sshtunnel / manual SSH (local dev only) |
| Production server | Nginx + systemd |

---

## Prerequisites

Make sure the following are installed before starting:

**On your laptop (Windows):**
- Python 3.11 or higher — https://www.python.org/downloads/
- Node.js 20 or higher — https://nodejs.org/
- Git — https://git-scm.com/
- VS Code (recommended) — https://code.visualstudio.com/

**Access credentials (get from your admin):**
- Database: host, port, name, username, password
- SSH tunnel (local dev): bastion host IP, SSH username, private key file

---

## Local Development Setup

### 1. Clone the repository

```powershell
git clone <your-repo-url>
cd Dashboard_project
```

### 2. Set up the Python virtual environment

```powershell
python -m venv venv
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned)
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` at the start of your terminal line.

### 3. Install backend dependencies

```powershell
cd backend
pip install fastapi uvicorn pandas psycopg2-binary python-dotenv python-jose passlib numpy sshtunnel paramiko openpyxl
pip freeze > requirements.txt
```

### 4. Configure backend environment variables

Create a file called `.env` inside the `backend/` folder:

```dotenv
DB_HOST=localhost
DB_PORT=5933
DB_NAME=your_database_name
DB_USER=your_database_username
DB_PASSWORD=your_database_password
```

> **Note:** When using SSH tunnel locally, set `DB_HOST=localhost` and `DB_PORT` to the tunnel's local forwarded port (5933 in this project). When deployed on a server with direct DB access, set `DB_HOST` to the actual database host.

### 5. Set up the SSH tunnel (local development only)

The database (AWS RDS) is not publicly accessible. You must open an SSH tunnel before running the backend locally.

**Fix key file permissions first (run once):**
```powershell
icacls "C:\path\to\datanalyst-kalyan-livedb" /inheritance:r /grant:r "$($env:USERNAME):(R)"
```

**Open the tunnel in a dedicated terminal (keep it open):**
```powershell
ssh -i "C:\path\to\datanalyst-kalyan-livedb" -L 5933:your-rds-host.rds.amazonaws.com:5933 datanalyst@BASTION_IP -N
```

The terminal should sit silently with no output — this means the tunnel is active.

> **On the production server:** No tunnel needed. The server has direct network access to the database. Skip this step entirely.

### 6. Test the database connection

With the SSH tunnel running, test the full data pipeline:

```powershell
cd backend
python data_loader.py
```

Expected output:
```
[db] Connecting to localhost:5933/your_db ...
[db] Fetching data from 2026-04-30 to 2026-05-30
[db] Query started — fetching 30 days of data ...
[db] Fetched 1,438,824 rows ...
[clean] 1,438,824 rows after cleaning
[build] branchwise: 1,044 rows
[build] languagewise: 859 rows
[ready] Data loaded from database.
```

If you see errors, check the Troubleshooting section below.

### 7. Start the backend server

```powershell
cd backend
uvicorn main:app --reload --port 8000
```

Expected output:
```
[startup] Loading data from database …
[startup] Ready.
INFO: Uvicorn running on http://127.0.0.1:8000
```

Verify it's working at: `http://localhost:8000/health`

### 8. Install frontend dependencies

Open a new PowerShell terminal:

```powershell
cd frontend
npm install
```

### 9. Configure frontend environment variables

Create or update `frontend/.env`:

```dotenv
VITE_API_URL=http://localhost:8000
VITE_LOGIN_USERNAME=admin
VITE_LOGIN_PASSWORD=marketsof1@2026
```

> **Note:** `VITE_LOGIN_USERNAME` and `VITE_LOGIN_PASSWORD` are the fallback credentials. Actual user management is handled through the Admin page in the dashboard.

### 10. Start the frontend

```powershell
cd frontend
npm run dev
```

Open your browser at: `http://localhost:5173`

---

## Production Deployment

### 1. Update environment variables

**`backend/.env`** — use the direct DB host (no tunnel needed on server):
```dotenv
DB_HOST=your_actual_db_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_username
DB_PASSWORD=your_database_password
```

**`frontend/.env`** — point to the server's public IP:
```dotenv
VITE_API_URL=http://YOUR_SERVER_IP:8000
```

### 2. Build the frontend

```powershell
cd frontend
npm run build
```

This creates a `frontend/dist/` folder with the production-ready static files.

### 3. Upload to server

```powershell
# Upload backend
scp -i "path/to/key.pem" -r backend ubuntu@YOUR_SERVER_IP:~/dashboard/

# Upload built frontend
scp -i "path/to/key.pem" -r frontend/dist ubuntu@YOUR_SERVER_IP:~/dashboard/frontend_dist/
```

### 4. Install server dependencies

SSH into the server, then:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx -y

cd ~/dashboard/backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pandas psycopg2-binary python-dotenv python-jose passlib numpy openpyxl
```

### 5. Run backend as a service

```bash
sudo nano /etc/systemd/system/dashboard.service
```

Paste this (replace `ubuntu` with your server username):

```ini
[Unit]
Description=Marketsof1 Sales Dashboard API
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

Visit `http://YOUR_SERVER_IP` — the login page should appear.

---

## Authentication

The dashboard requires login. All routes are protected.

**Default credentials:**
```
Username : admin
Password : marketsof1@2026
```

- Credentials are validated against `backend/users.json`
- On successful login a JWT token is issued (valid 8 hours)
- Token is stored in `sessionStorage` — clears when the browser tab is closed
- Admin users see a **Users** button in the navbar to manage accounts

---

## API Endpoints

All endpoints are available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server status + available filter values |
| `POST` | `/auth/login` | Login — returns JWT token |
| `GET` | `/auth/users` | List all users (admin only) |
| `POST` | `/auth/users` | Add a new user (admin only) |
| `DELETE` | `/auth/users/{username}` | Delete a user (admin only) |
| `GET` | `/charts/branch/call-count` | Daily call count — branchwise |
| `GET` | `/charts/branch/talk-time` | Daily talk time — branchwise |
| `GET` | `/charts/lang/call-count` | Daily call count — languagewise |
| `GET` | `/charts/lang/talk-time` | Daily talk time — languagewise |
| `GET` | `/charts/lang/connected-count` | Daily connected calls — languagewise |
| `GET` | `/filters` | Cascading filter options |

---

## Charts and Filters

Five charts are available from the home page:

**Branchwise (2 charts):**
- Call Count per day
- Talk Time per day

Filters: `branch`, `dialer`, `agentname (teamname)`

**Languagewise (3 charts):**
- Call Count per day
- Talk Time per day
- Connected Call Count per day

Filters: `branch`, `language`, `agentname (teamname)`

Filters are **cascading** — selecting a branch automatically updates the dialer/language and agent dropdowns to only show values that exist within that branch. This prevents empty results.

---

## User Management

Admin users can manage accounts from the **Users** page (navbar top-left):

- **Add user** — enter username and password (min 6 characters). New users always get the `user` role.
- **Delete user** — removes the user immediately. The `admin` account cannot be deleted.
- Changes are saved to `backend/users.json` instantly.

---

## Data Pipeline

Data flows through 5 stages every time the server starts:

```
PostgreSQL DB (30 days of call logs)
        ↓
    _fetch_from_db()     Phase 1 — psycopg2 query
        ↓
    _clean()             Phase 2 — fix nulls, reassign doocti/Unknown → Kochi
        ↓
    _build_branch()      Phase 3 — group by date/branch/dialer/teamname
    _build_lang()        Phase 3 — group by date/branch/language/teamname
        ↓
    RAM cache            Stored in memory — no re-reading on each request
        ↓
    FastAPI endpoints    Filter + group by date on the fly per request
        ↓
    React + Recharts     Bar chart rendered in browser
```

The date range (last 30 days) is computed automatically on every server startup — no manual date changes needed.

---

## Troubleshooting

**SSH tunnel permission denied:**
```powershell
icacls "path\to\key" /inheritance:r /grant:r "$($env:USERNAME):(R)"
```

**DB connection timeout:**
- Check the SSH tunnel is running in a separate terminal
- Verify `DB_HOST=localhost` in `backend/.env` when using tunnel

**`recharts` not found:**
```powershell
cd frontend && npm install recharts
```

**`python-jose` not found:**
```powershell
pip install python-jose passlib
```

**Frontend shows blank page after login:**
- Check browser console for errors
- Confirm `VITE_API_URL=http://localhost:8000` in `frontend/.env`
- Confirm backend is running and `/health` returns `"status": "ok"`

**Backend query timeout (30-day data too slow):**
- Reduce days temporarily in `data_loader.py`: `timedelta(days=7)`
- Confirm with 7 days then increase back to 30

**Nginx 502 Bad Gateway on server:**
```bash
sudo systemctl status dashboard      # check if backend is running
sudo journalctl -u dashboard -f      # view backend logs
sudo systemctl restart dashboard     # restart if needed
```

---

## Important Notes

- Never commit `.env` files or the SSH private key to Git. Add them to `.gitignore`:
  ```
  backend/.env
  frontend/.env
  data/datanalyst-kalyan-livedb
  ```
- `users.json` contains plaintext passwords. In a future version this should use hashed passwords.
- The JWT secret key in `auth.py` should be changed to a long random string in production.
- The SSH tunnel approach is for **local development only**. The production server connects directly to the database.