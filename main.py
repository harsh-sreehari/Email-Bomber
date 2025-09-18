from fastapi import FastAPI
from pydantic import BaseModel
import smtplib
from email.message import EmailMessage
import os
import random
import time
import json
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Load environment variables
load_dotenv()

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")


class EmailRequest(BaseModel):
    receiver_email: str  # Only input needed from user


# Utility function: Load subjects/messages from JSON file
def load_messages():
    try:
        with open("templates/messages.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("subjects", []), data.get("messages", [])
    except Exception as e:
        print("Error loading messages.json:", e)
        return [], []


@app.post("/send_email/")
async def send_email(request: EmailRequest):
    try:
        # Number of sender emails available
        email_count = 2  # <--- Change if you have more/less accounts

        # Collect sender accounts from environment
        senders = []
        for i in range(1, email_count + 1):
            email = os.getenv(f"SENDER_EMAIL_{i}")
            password = os.getenv(f"SENDER_PASSWORD_{i}")
            if not email or not password:
                return {"status": "error", "message": f"Missing sender {i} credentials"}
            senders.append((email, password))

        # Load subjects & messages from file
        subjects, messages = load_messages()
        if not subjects or not messages:
            return {"status": "error", "message": "No subjects/messages available"}

        total_messages = 15  # Send exactly 15 messages
        count = 0

        while count < total_messages:
            count += 1

            # Select random subject & message
            subject = random.choice(subjects) + f" #{count}"
            message = random.choice(messages)

            # Pick sender email in round-robin
            sender_email, sender_password = senders[count % email_count]

            # Prepare email
            msg = EmailMessage()
            msg.set_content(message)
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = request.receiver_email

            # Send email
            with smtplib.SMTP("smtp.gmail.com", 587) as mail_server:
                mail_server.ehlo()
                mail_server.starttls()
                mail_server.login(sender_email, sender_password)
                mail_server.send_message(msg)

            # Faster sending
            time.sleep(0.5)

        return {"status": "success", "message": f"{total_messages} emails sent successfully ✅"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


# Serve HTML page
@app.get("/")
async def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
