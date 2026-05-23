import os
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
FROM_EMAIL = "braydenfisk@gmail.com"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str


@app.post("/send-email")
async def send_email(req: EmailRequest):
    if not GMAIL_APP_PASSWORD:
        raise HTTPException(status_code=500, detail="GMAIL_APP_PASSWORD is not configured.")

    msg = MIMEText(req.body)
    msg["Subject"] = req.subject
    msg["From"] = FROM_EMAIL
    msg["To"] = req.to

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(FROM_EMAIL, GMAIL_APP_PASSWORD)
            server.sendmail(FROM_EMAIL, req.to, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to send email: {str(e)}")

    return {"status": "ok"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
