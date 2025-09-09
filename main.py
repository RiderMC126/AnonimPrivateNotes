from fastapi import FastAPI, Request, Form, HTTPException, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import logging
import asyncio
import uvicorn
import sys
import secrets
import string
import sqlite3
import os
from db import init_db
from utils import *


# Application initialization
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


key_file = 'encryption_key.key'
if os.path.exists(key_file):
    with open(key_file, 'rb') as f:
        key = f.read()
else:
    key = Fernet.generate_key()
    with open(key_file, 'wb') as f:
        f.write(key)
cipher = Fernet(key)


# main page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "AnonimPrivateNotes"}
    )

# about page
@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(
        "about.html", 
        {"request": request, "title": "Как это работает?"}
    )

# support page
@app.get("/support", response_class=HTMLResponse)
async def support(request: Request):
    return templates.TemplateResponse(
        "support.html", 
        {"request": request, "title": "Контакты"}
    )

# support page
@app.get("/donate", response_class=HTMLResponse)
async def donate(request: Request):
    return templates.TemplateResponse(
        "donate.html", 
        {"request": request, "title": "Поддержать"}
    )

# Create note
@app.post("/create")
async def create_note(
    request: Request,
    text: str = Form(None),
    file_upload: UploadFile = File(None),
    expiry_time: str = Form(...),
    conn: sqlite3.Connection = Depends(get_db)
):
    if not text and (not file_upload or file_upload.filename == ""):
        raise HTTPException(status_code=422, detail="Text or file must be provided")

    content = ""
    if file_upload and file_upload.filename != "":
        file_content = await file_upload.read()  
        content = file_content.decode('utf-8', errors='ignore') 
        logger.info(f"File uploaded: {file_upload.filename}, content length: {len(content)}")
    elif text:
        content = text.strip()
        logger.info(f"Text content length: {len(content)}")
    
    if not content:
        raise HTTPException(status_code=422, detail="Content cannot be empty")

    note_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))
    
    encrypted_content = cipher.encrypt(content.encode('utf-8')).decode('utf-8')
    logger.info(f"Note ID {note_id} created, content encrypted")
    
    expiry_map = {
        "5 минут": 5 / (60 * 24), 
        "15 минут": 15 / (60 * 24),  
        "30 минут": 30 / (60 * 24), 
        "1 час": 1 / 24,
        "2 часа": 2 / 24,
        "12 часов": 12 / 24,
        "1 день": 1,
        "2 дня": 2,
        "7 дней": 7
    }
    expiry_days = expiry_map.get(expiry_time, 1) 
    delete_date = datetime.now() + timedelta(days=expiry_days)
    
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO records (id, content, delete_date, counter)
        VALUES (?, ?, ?, ?)
        ''',
        (note_id, encrypted_content, delete_date.isoformat(), 0)
    )
    conn.commit()
    
    note_url = f"/note/{note_id}"
    
    return JSONResponse(content={"note_url": note_url})

# note page
@app.get("/note/{note_id}", response_class=HTMLResponse)
async def view_note(request: Request, note_id: str, conn: sqlite3.Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute('SELECT content, delete_date, counter FROM records WHERE id = ?', (note_id,))
    note = cursor.fetchone()
    
    if not note:
        logger.error(f"Note not found for ID: {note_id}")
        raise HTTPException(status_code=404, detail="Записка не найдена")
    
    content, delete_date, counter = note
    
    try:
        if isinstance(delete_date, str):
            delete_date = datetime.fromisoformat(delete_date)
        elif isinstance(delete_date, datetime):
            pass 
        else:
            delete_date = datetime.fromisoformat(str(delete_date))
    except ValueError as e:
        logger.error(f"Invalid date format for note {note_id}: {delete_date}")
        delete_date = datetime.now() + timedelta(days=1) 
    
    if datetime.now() > delete_date:
        logger.info(f"Note expired for ID: {note_id}, delete_date: {delete_date}")
        cursor.execute('DELETE FROM records WHERE id = ?', (note_id,))
        conn.commit()
        raise HTTPException(status_code=410, detail="Записка истекла")
    
    logger.info(f"Processing note ID: {note_id}")
    
    try:
        decrypted_content = cipher.decrypt(content.encode('utf-8')).decode('utf-8')
        logger.info(f"Successfully decrypted note {note_id}, content length: {len(decrypted_content)}")
    except Exception as e:
        logger.error(f"Decryption failed for ID {note_id}: {str(e)}")
        try:
            decrypted_content = cipher.decrypt(content).decode('utf-8')
            logger.info(f"Successfully decrypted note {note_id} with alternative method")
        except:
            raise HTTPException(status_code=500, detail="Ошибка при расшифровке записки")
    
    cursor.execute('UPDATE records SET counter = counter + 1 WHERE id = ?', (note_id,))
    conn.commit()
    
    cursor.execute('DELETE FROM records WHERE id = ?', (note_id,))
    conn.commit()
    
    logger.info(f"Note {note_id} viewed and deleted, content: {decrypted_content[:50]}...")
    
    return templates.TemplateResponse(
        "note.html",
        {"request": request, "content": decrypted_content, "title": "Ваша записка"}
    )


# Start application
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    init_db()
    uvicorn.run("main:app", host="127.0.0.1", port=3000, reload=True)