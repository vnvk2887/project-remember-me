# app.py - minimal demo API that uses data.db
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import sqlite3
import datetime

DB_PATH = "data.db"
app = FastAPI(title="RememberMe Demo")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def startup():
    conn = get_conn()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS opportunities (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, source TEXT, created_at TEXT)"
    )
    conn.commit()
    conn.close()

@app.get("/api/opportunities")
def list_opportunities():
    conn = get_conn()
    cur = conn.execute("SELECT id, title, source, created_at FROM opportunities ORDER BY id DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return JSONResponse(rows)

@app.post("/api/upload_whatsapp")
async def upload_whatsapp(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    content = await file.read()
    try:
        text = content.decode("utf-8", errors="ignore")
    except Exception:
        text = content.decode("latin-1", errors="ignore")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        raise HTTPException(status_code=400, detail="Uploaded file contains no text lines")
    conn = get_conn()
    now = datetime.datetime.utcnow().isoformat()
    inserted = 0
    for line in lines:
        cur = conn.execute("SELECT 1 FROM opportunities WHERE title = ? LIMIT 1", (line,))
        if cur.fetchone():
            continue
        conn.execute(
            "INSERT INTO opportunities (title, source, created_at) VALUES (?, ?, ?)",
            (line[:1000], "upload", now),
        )
        inserted += 1
    conn.commit()
    conn.close()
    return {"inserted": inserted, "total_lines": len(lines)}
