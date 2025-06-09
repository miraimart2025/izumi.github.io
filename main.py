from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContactForm(BaseModel):
    name: str
    email: str
    message: str

# Google Sheets API の認証
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# 環境変数からJSON文字列を取得し辞書に変換
json_keyfile_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])

# 認証
creds = ServiceAccountCredentials.from_json_keyfile_dict(json_keyfile_dict, scope)
client = gspread.authorize(creds)

# スプレッドシートを開く
spreadsheet = client.open("問い合わせ一覧")
sheet = spreadsheet.sheet1

@app.post("/contact")
def receive_contact(form: ContactForm):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([form.name, form.email, form.message, now])
    return {"message": "スプレッドシートに保存しました！"}
