from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import logging
import asyncio
import uvicorn
import sys
import secrets
import string
from datetime import datetime, timedelta

# Application initialization
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Хранилище записок (в реальном приложении используйте базу данных)
notes_storage = {}

def generate_note_id():
    """Генерация уникального ID для записки"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))

# main page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # ИСПРАВЛЕНО: правильный синтаксис для TemplateResponse
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "AnonimPrivateNotes"}
    )

@app.post("/create", response_class=HTMLResponse)
async def create_note(
    request: Request,
    text: str = Form(...),
    expiry_time: str = Form(default="7"),
):
    """Создание новой записки"""
    
    if not text.strip():
        raise HTTPException(status_code=400, detail="Текст записки обязателен")
    
    # Генерируем ID записки
    note_id = generate_note_id()
    
    # Определяем время истечения
    expiry_mapping = {
        "30 минут": 0.5,
        "1 час": 1,
        "1 день": 24,
        "7 дней": 168
    }
    
    hours = expiry_mapping.get(expiry_time, 168)
    expiry_date = datetime.now() + timedelta(hours=hours)
    
    # Сохраняем записку
    notes_storage[note_id] = {
        "text": text,
        "created_at": datetime.now(),
        "expires_at": expiry_date,
        "read": False
    }
    
    # Возвращаем страницу с ссылкой на записку
    note_url = f"{request.base_url}note/{note_id}"
    return templates.TemplateResponse(
        "created.html",
        {"request": request, "note_url": note_url, "note_id": note_id}
    )

@app.get("/note/{note_id}", response_class=HTMLResponse)
async def view_note(request: Request, note_id: str):
    """Просмотр записки (одноразовый)"""
    
    if note_id not in notes_storage:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Записка не найдена"}
        )
    
    note = notes_storage[note_id]
    
    # Проверяем, не истекла ли записка
    if datetime.now() > note["expires_at"]:
        del notes_storage[note_id]
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Записка истекла"}
        )
    
    # Проверяем, не была ли записка уже прочитана
    if note["read"]:
        del notes_storage[note_id]
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Записка уже была прочитана"}
        )
    
    # Помечаем как прочитанную и удаляем
    note_content = note["text"]
    del notes_storage[note_id]
    
    return templates.TemplateResponse(
        "note.html",
        {"request": request, "note_content": note_content}
    )

@app.get("/api/notes/count")
async def get_notes_count():
    """API для получения количества активных записок"""
    return {"count": len(notes_storage)}

# Очистка истёкших записок
def cleanup_expired_notes():
    """Удаление истёкших записок"""
    current_time = datetime.now()
    expired_notes = [
        note_id for note_id, note in notes_storage.items()
        if current_time > note["expires_at"]
    ]
    
    for note_id in expired_notes:
        del notes_storage[note_id]
    
    return len(expired_notes)

@app.get("/cleanup")
async def manual_cleanup():
    """Ручная очистка истёкших записок"""
    cleaned = cleanup_expired_notes()
    return {"message": f"Удалено {cleaned} истёкших записок"}

# Start application
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    uvicorn.run("main:app", host="127.0.0.1", port=3000, reload=True)