import os
import resend
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
FROM_EMAIL = "onboarding@resend.dev"


class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str


@app.post("/send-email")
async def send_email(req: EmailRequest):
    if not RESEND_API_KEY:
        raise HTTPException(status_code=500, detail="RESEND_API_KEY is not configured.")

    resend.api_key = RESEND_API_KEY

    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [req.to],
            "subject": req.subject,
            "text": req.body,
        })
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to send email: {str(e)}")

    return {"status": "ok"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
