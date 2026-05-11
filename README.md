<div align="center">

![header](https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:0077B6,100:00B4D8&height=200&section=header&text=SwimScore&fontSize=60&fontColor=ffffff&fontAlignY=38&desc=Live%20Results%20%C2%B7%20Scoreboard%20%C2%B7%20Admin%20Panel%20%C2%B7%20Secure&descSize=18&descAlignY=58&descColor=b0c4de)

<br/>

<!-- Fancy Badges -->
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-Templates-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-Styled-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![License](https://img.shields.io/badge/License-ISC-blue?style=for-the-badge)

<br/>

<img src="https://img.shields.io/badge/spaghetti%20code-yes-success?logo=java" alt="Spaghetti code: yes">
<img src="https://img.shields.io/badge/Runs%20On-Vibes%20%26%20Prayers-ff69b4" alt="Runs on vibes & prayers">
<img src="https://img.shields.io/badge/Tests-Who%20Needs%20'Em-red" alt="Tests: who needs 'em">
<img src="https://img.shields.io/github/repo-size/Toaster496/swim-app" alt="Repo Size">
<img src="https://img.shields.io/github/last-commit/Toaster496/swim-app?logo=git" alt="Last commit">
<img src="https://img.shields.io/github/stars/Toaster496/swim-app" alt="Stars">
<img src="https://img.shields.io/github/issues/Toaster496/swim-app" alt="Issues">

<br/><br/>

**A full-stack Flask web application for live swim meet scoring — featuring real-time results, a public scoreboard, role-based admin panel, and 2FA security.**

[Features](#-features) · [Tech Stack](#-tech-stack) · [Installation](#-installation) · [Project Structure](#-project-structure) · [Usage](#-usage-guide) · [API](#-api-endpoints) · [Contributing](#-contributing)

</div>

---

## ✨ Features

<table>
<tr>
<td width="33%" valign="top">

### 🏊 Live Results
- Real-time swim results page
- Filter by **meet**, **gender**, & **search**
- Automatic ranking & delta times
- Paginated athlete view
- Auto-refresh via JSON API

</td>
<td width="33%" valign="top">

### 📊 Scoreboard
- Public-facing scoreboard display
- Event-based navigation
- Reaction time tracking
- Points & rank calculation
- Clean, readable layout

</td>
<td width="33%" valign="top">

### 🔐 Admin Panel
- Role-based access (**Admin**, **Timekeeper**, **Viewer**)
- Manage events, athletes, & users
- Audit logging with severity levels
- System settings dashboard
- Secure password policies

</td>
</tr>
</table>

<table>
<tr>
<td width="50%" valign="top">

### 🛡️ Security
- **2FA** with email-based OTP
- Password hashing via Werkzeug
- Session timeout controls
- IP change detection
- Configurable password requirements

</td>
<td width="50%" valign="top">

### ⚡ Deployment
- One-command Railway/Heroku deploy
- Gunicorn production server
- SQLite (dev) or any SQL database
- `.env`-based configuration
- Auto-seeding of default admin

</td>
</tr>
</table>

---

## 🛠️ Tech Stack

```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                             │
│         HTML5 · CSS3 · Vanilla JS · Jinja2 Templates        │
└────────────────────────┬────────────────────────────────────┘
                         │  HTTP
┌────────────────────────▼────────────────────────────────────┐
│                    Flask Application                        │
│   Auth · Admin · Viewer · Blueprints · Flask-Login          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                SQLAlchemy + SQLite / PostgreSQL              │
│     Users · Events · Athletes · Audit Logs · Settings       │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Runtime | Python 3.10+ | Server environment |
| Framework | Flask 3.x | HTTP routing, templates, blueprints |
| ORM | Flask-SQLAlchemy | Database models & queries |
| Auth | Flask-Login + Werkzeug | Session management & password hashing |
| Database | SQLite (default) | Persistent data storage |
| Server | Gunicorn | Production WSGI server |
| Frontend | Jinja2 / HTML5 / CSS3 | Templating & styling |

---

## 🚀 Installation

### Prerequisites
- [Python](https://python.org/) 3.10 or higher
- pip (bundled with Python)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/Toaster496/swim-app.git
cd swim-app

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your config (or leave defaults for local dev)

# 5. Start the server
python app.py
```

Open **http://localhost:5000** in your browser.

> **Default Admin Login:**
> Username: `admin` · Password: `Admin1234!`

---

## 📂 Project Structure

```
swim-app/
├── swimapp/
│   ├── __init__.py         # App factory, config, db init
│   ├── models.py           # User, Event, Athlete, AuditLog, SystemSetting
│   ├── auth.py             # Login, logout, 2FA OTP flow
│   ├── admin.py            # Admin panel — manage events, users, settings
│   ├── viewer.py           # Public live results + scoreboard
│   ├── static/             # CSS, JS, and assets
│   └── templates/
│       ├── base.html       # Shared layout
│       ├── admin_base.html # Admin layout with sidebar
│       ├── auth/           # Login & OTP templates
│       ├── admin/          # Dashboard, events, users, logs, settings
│       └── viewer/         # Live results & scoreboard pages
├── instance/
│   └── swim.db             # SQLite database (auto-created)
├── app.py                  # Entry point
├── requirements.txt        # Python dependencies
├── Procfile                # Gunicorn deploy config
├── .env.example            # Sample environment variables
└── README.md               # This file
```

---

## 📖 Usage Guide

### 🏁 Live Results (`/live`)
1. Navigate to the **Live** page
2. Use the **Meet** and **Gender** dropdowns to filter events
3. Search for athletes by name or team
4. Results auto-refresh with ranks, times, and deltas

### 📋 Scoreboard (`/scoreboard`)
1. Select an active event from the dropdown
2. View ranked athletes with times and points
3. Perfect for displaying on a big screen at meets

### ⚙️ Admin Panel (`/admin`)
1. Log in with admin credentials
2. Complete 2FA via email OTP (or check console in dev mode)
3. Manage **Events** — create, edit, activate/deactivate
4. Manage **Athletes** — assign lanes, enter times, auto-rank
5. Manage **Users** — create timekeepers, set roles
6. View **Audit Logs** — track all admin actions
7. Configure **System Settings** — password policies, session timeouts, 2FA rules

---

## 🔌 API Endpoints

### `GET /api/live`
Fetch live athlete data for auto-refresh.

```json
// Request
GET /api/live?event_id=1

// Response
{
  "data": [
    {
      "id": 1,
      "lane": 4,
      "name": "John Smith",
      "team": "Dolphins",
      "time": "52.34",
      "rank": 1,
      "delta": "--",
      "points": 10,
      "reaction_time": "0.68"
    }
  ],
  "last_updated": "12:34:56 UTC"
}
```

| Method | Endpoint | Operation |
|--------|----------|-----------|
| `GET` | `/live` | Live results page with filters |
| `GET` | `/scoreboard` | Public scoreboard display |
| `GET` | `/api/live` | JSON athlete data for auto-refresh |
| `POST` | `/admin/*` | Admin CRUD operations (auth required) |

---

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the **ISC License**. See [`LICENSE`](LICENSE) for details.

---

<div align="center">

![footer](https://capsule-render.vercel.app/api?type=waving&color=0:00B4D8,50:0077B6,100:0d1117&height=100&section=footer)

Built with 🏊 by [Toaster496](https://github.com/Toaster496) using Flask & Python

*"It's not a bug, it's a feature"* - Every developer ever

</div>
