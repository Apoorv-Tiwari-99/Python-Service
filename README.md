# 🐍 Personal Finance Tracker – Python Service

This is the **Python microservice** for *Personal Finance Tracker+*.  
It provides **smart suggestions** based on user expense data, using Flask and Pandas, and is meant to be used together with the backend + frontend.

---

## 📦 What’s in this repo

| Item | Purpose |
|---|---|
| `run.py` | Entry point to start the Flask app. |
| `app/` | Folder for your Flask application modules (routes, logic, etc.). |
| `requirements.txt` | List of Python dependencies. |
| `gunicorn.conf.py` | Configuration for Gunicorn server. |
| `Procfile` | Used by deployment platforms to define how to start the service. |
| `.python-version` | Python version used (if you are using pyenv or similar). |

---

## ✨ Features

- Exposes an HTTP API (via Flask) that accepts expense data (JSON)  
- Uses Pandas for data analysis / aggregation  
- Generates suggestions / insights based on user spending patterns (e.g. top categories, trend changes)  
- Configured to run with Gunicorn for production deployment

---

## 🛠️ Tech Stack

- Python 3.x  
- Flask  
- Pandas  
- Gunicorn  
- Additional typical libs (from `requirements.txt`)  

---

## ⚙️ Setup & Running Locally

1. **Clone the repo**

   ```bash
  git clone https://github.com/Apoorv-Tiwari-99/Python-Service.git
  cd Python-Service
  
2.  Install dependencies
   pip install -r requirements.txt

3. Run the service
   python run.py

 🔑 Environment Variables
 
FLASK_ENV=development
PORT=5001                 # or whichever port you wish the service to listen on
BACKEND_URL=your_backend_api_url 


   git clone https://github.com/Apoorv-Tiwari-99/Python-Service.git
   cd Python-Service
