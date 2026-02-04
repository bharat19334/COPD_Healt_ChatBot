import os
import google.generativeai as genai
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import uvicorn
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 1. SETUP
load_dotenv()
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    # Emojis hata diye taaki error na aaye
    print("[ERROR] API Key nahi mili! .env file check karein.")
else:
    print("[SUCCESS] API Key loaded successfully.")

# 2. AI CONFIGURATION
genai.configure(api_key=GOOGLE_API_KEY)

# Safety Settings: Taaki AI 'Medical Advice' ke naam par dar kar block na kare
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# Configuration
generation_config = genai.types.GenerationConfig(
    max_output_tokens=300, 
    temperature=0.7
)

# 3. SYSTEM INSTRUCTION
SYSTEM_INSTRUCTION = """
ROLE: Tumhara naam 'COPD Assistant' hai. Tum ek expert COPD Health Assistant ho.
GUIDELINES: 
- Hinglish mein baat karo. 
- Jawab short (5-7 lines) mein do.
- Dawai (Medicine) prescribe mat karo.
- Agar koi serious symptom bataye to bolo 'Turant Doctor ke paas jao'.
- Iske mukhya symptoms hain: lagatar khansi, balgham aur saans phoolna.
- Sabse bada risk factor smoking hai. Smoking band karna sabse important step hai.
- Healthy khana khaayein aur paani bharpur piyein.
- Saans phoolne par calmly baith jaayein, pursed-lip breathing try karein.
- Yaad rakhein, main ek chatbot hoon, doctor nahi.
- Agar koi copd se related nhi ho toh usse bolo ki ye copd se related nhi hai aur main sirf COPD health assist karta hu.
- End mein ek chhota encouraging note likho.
"""

# NOTE: 'gemini-1.5-flash' use kar rahe hain (Ye stable hai)
model = genai.GenerativeModel(
    'gemini-1.5-flash', 
    safety_settings=safety_settings,
    generation_config=generation_config,
    system_instruction=SYSTEM_INSTRUCTION
)

# 4. SERVER SETUP
app = FastAPI()

@app.post("/whatsapp")
async def reply_whatsapp(Body: str = Form(...), From: str = Form(...)):
    user_message = Body.strip()
    sender_number = From

    # Console log bina emoji ke
    print(f"[Message] From {sender_number}: {user_message}")

    try:
        # Har user ke liye fresh chat session (Privacy ke liye zaroori)
        chat = model.start_chat(history=[])
        
        response = chat.send_message(user_message)
        
        if response.text:
            ai_reply_text = response.text
        else:
            ai_reply_text = "Maaf karein, main iska jawab nahi de sakta (Safety Policy)."
            
        print(f"[AI Reply] Sent successfully.")

    except Exception as e:
        print(f"[ERROR] {e}")
        ai_reply_text = "Server abhi busy hai. Kripya thodi der baad try karein."

    # Twilio Response Container
    twilio_resp = MessagingResponse()
    twilio_resp.message(ai_reply_text)

    # XML Format Return
    return Response(content=str(twilio_resp), media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
