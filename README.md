# LineLink Backend

**Production tracking backend for manufacturing operations.**

LineLink is a Python-based backend designed to track production progress, manage manufacturing data, and provide structured information for shop-floor decision-making.

## Overview

LineLink addresses the challenge of tracking production progress through manual and disconnected processes.

The system provides a centralized backend for:

- 📊 Production progress tracking
- 🏭 Manufacturing workflow management
- 🗄️ Structured production data
- 🔌 REST API access
- 🧪 Automated testing
- ☁️ Cloud deployment

## Technology Stack

| Technology | Purpose |
|---|---|
| 🐍 **Python** | Backend development |
| 🗄️ **SQL** | Relational database |
| 🔌 **REST API** | Application communication |
| 🧪 **Pytest** | Automated testing |
| ⚙️ **GitHub Actions** | Continuous integration |
| ☁️ **Render** | Cloud deployment |

## Architecture

```text
┌──────────────────┐
│ Client / Frontend│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    REST API      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Python Backend  │
│  Business Logic  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   SQL Database   │
└──────────────────┘
```

The backend separates API routes, application logic, and database operations to support maintainability and future development.

## Key Features

### 📊 Production Tracking

Tracks manufacturing progress and provides structured access to production information.

### 🗄️ Database Management

Stores production information in a relational SQL database for consistent and queryable data.

### 🔌 REST API

Provides API endpoints for applications to interact with production data.

### 🧪 Automated Testing

Includes automated tests to validate backend functionality and reduce regressions.

### ⚙️ Continuous Integration

Uses GitHub Actions to automatically support testing during development.

### ☁️ Cloud Deployment

The backend is deployed to Render for access through a production environment.

## Project Structure

```text
LineLink-Backend/
│
├── app/
│   ├── routes/
│   ├── models/
│   └── ...
│
├── database/
│
├── tests/
│
├── .github/
│   └── workflows/
│
├── requirements.txt
├── run.py
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.x
- pip
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/ijromerob/LineLink-Backend.git
cd LineLink-Backend
```

### 2. Create a Virtual Environment

#### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python run.py
```

## Testing

Run the automated test suite with:

```bash
pytest
```

Tests are also integrated with GitHub Actions to support continuous integration.

## Production Environment

LineLink is deployed to a cloud environment using Render.

## Why LineLink?

LineLink was created from a manufacturing perspective, combining software development with practical production needs.

The project demonstrates how **manufacturing knowledge, software development, databases, and automation** can be combined to improve production visibility and support operational decision-making.

## Future Improvements

- 📊 Production dashboards
- ⚡ Real-time production updates
- 📈 KPI visualization
- 🔐 User authentication and authorization
- 📊 Expanded production analytics
- 🔗 Integration with additional manufacturing systems

## Author

**Ivan Romero**

*Industrial Engineering · Manufacturing · Software Development*
