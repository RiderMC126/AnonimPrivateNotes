from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from db import init_db
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



# main page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "AnonimPrivateNotes"}
    )

# about page
@app.get("/about", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "about.html", 
        {"request": request, "title": "Как это работает?"}
    )




# Start application
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(init_db())
    uvicorn.run("main:app", host="127.0.0.1", port=3000, reload=True)