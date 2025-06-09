from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # デプロイ後は制限可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# テンプレート & 静的ファイル
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Google Sheets認証
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("問い合わせ一覧").sheet1

# ページ表示
@app.get("/", response_class=HTMLResponse)
def get_we(request: Request):
    return templates.TemplateResponse("we.html", {"request": request})

@app.get("/thank-you", response_class=HTMLResponse)
def thank_you(request: Request):
    return templates.TemplateResponse("thank-you.html", {"request": request})

# フォーム処理
class ContactForm(BaseModel):
    name: str
    email: str
    message: str

@app.post("/contact")
def receive_contact(form: ContactForm):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([form.name, form.email, form.message, now])
    return {"message": "スプレッドシートに保存しました！"}
