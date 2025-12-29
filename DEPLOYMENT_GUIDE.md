# Eco-Sync Deployment Guide

## 🚀 Live URL
**Frontend**: `https://eco-sync-mvp.vercel.app` (or your specific URL)

## ⚠️ Database Limitation (Critical)
You are currently using **SQLite** (`eco_sync.db`). 
- **SQLite does not work well on Serverless (Vercel)** because the file system is ephemeral. 
- Every time the server restarts (which happens frequently), your database **resets** or becomes **read-only**.
- This is why you might see `500 Internal Server Error` on the live site.

### ✅ Solution: Use a Cloud Database (PostgreSQL)
To make your app fully functional on Vercel, switch to **Supabase** or **Neon**.

1. **Create a Database**: Go to [Supabase](https://supabase.com) and create a free project.
2. **Get Connection String**: Copy the credentials (e.g., `postgresql://user:pass@host:5432/db`).
3. **Update Vercel Environment Variables**:
   - Go to Vercel Dashboard -> Settings -> Environment Variables.
   - Add `DATABASE_URL` = `your_postgres_connection_string`.
4. **Update `database.py`**:
   - Install `psycopg2-binary`.
   - Ensure SQLAlchemy uses the new URL.

## 🛠️ Local Development
To run locally:
```bash
# Backend
cd backend
python uvicorn_run.py

# Frontend
cd frontend
# Open index.html with Live Server or Python http.server
```
