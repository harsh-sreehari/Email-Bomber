from fastapi import FastAPI
from pydantic import BaseModel
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

class EmailRequest(BaseModel):
    receiver_email: str
    subject: str
    message: str

@app.post("/send_email/")
async def send_email(request: EmailRequest):
    try:
        # Get credentials from environment variables
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")

        if not sender_email or not sender_password:
            return {"status": "error", "message": "Missing sender email or password in environment variables"}

        # Create email
        msg = EmailMessage()
        msg.set_content(request.message)
        msg["Subject"] = request.subject
        msg["From"] = sender_email
        msg["To"] = request.receiver_email

        # Connect to Gmail SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as mail_server:
            mail_server.ehlo()
            mail_server.starttls()
            mail_server.login(sender_email, sender_password)
            mail_server.send_message(msg)

        return {"status": "success", "message": "Email sent successfully ✅"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# Default route to serve the email client HTML
@app.get("/")
async def root():
    return FileResponse("static/index.html")