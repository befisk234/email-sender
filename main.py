import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
FROM_EMAIL = os.environ.get("FROM_EMAIL")


class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str


@app.post("/send-email")
async def send_email(req: EmailRequest):
    if not SENDGRID_API_KEY:
        raise HTTPException(status_code=500, detail="SENDGRID_API_KEY is not configured.")
    if not FROM_EMAIL:
        raise HTTPException(status_code=500, detail="FROM_EMAIL is not configured.")

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=req.to,
        subject=req.subject,
        plain_text_content=req.body,
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail="SendGrid rejected the request.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to send email: {str(e)}")

    return {"status": "ok"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
