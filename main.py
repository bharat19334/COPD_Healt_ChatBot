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
    # Emojis hata diye taaki Windows par crash na ho
    print("[ERROR] API Key nahi mili! .env file check karein.")
else:
    print("[SUCCESS] API Key loaded successfully.")

# 2. AI CONFIGURATION (Stable & Safe)
genai.configure(api_key=GOOGLE_API_KEY)

# Safety Settings
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# Configuration
generation_config = genai.types.GenerationConfig(
    max_output_tokens=200, 
    temperature=0.7
)

# IMPORTANT: Model 'gemini-1.5-flash' kar diya hai (Best for WhatsApp)
model = genai.GenerativeModel(
    'gemini-2.5-flash', 
    safety_settings=safety_settings,
    generation_config=generation_config
)

# 3. SYSTEM INSTRUCTION
SYSTEM_INSTRUCTION = """
ROLE: Tumhara naam 'LungGuard' hai. Tum ek expert COPD Health Assistant ho.
GUIDELINES: 
- Hinglish mein baat karo. 
- Jawab short (2-3 lines) mein do.
- Dawai (Medicine) prescribe mat karo.
- Agar koi serious symptom bataye to bolo 'Turant Doctor ke paas jao'.
- Iske mukhya symptoms hain: lagatar khansi, balgham aur saans phoolna.
- Sabse bada risk factor smoking hai, lekin pollution se bhi ho sakta hai.
- Smoking band karna sabse important step hai.agar aapko shaas lene main takleef aati ho toh.
- Healthy khana khaayein aur paani bharpur piyein.
- Saans phoolne par calmly baith jaayein, pursed-lip breathing try karein.
- COPD ke liye spirometry test confirm karta hai.
- Dawaai kabhi bhi aapne aap band nahi karni hai.
- Yaad rakhein, main ek chatbot hoon, doctor nahi.
- Khana khate samay saans phoole toh chhote bites lein, aaraam se.
- Oxygen therapy ki zaroorat padh sakti hai, doctor se baat karein.
- Sleeping position: head up rakhke sone se saans lena aasan ho jaata hai.
- Cooking karte waqt chimney ON rakhein taaki smoke na phoonke.
- Yoga ke breathing exercises (pranayama) doctor ki advice se shuru karein.
- Agar weight kam ho raha hai toh protein-rich diet lein.
- Saans phoolne par ghabrayein nahi, slow-breathing exercises karein.
- Naye symptoms aayein (jaise pairon mein swelling) toh doctor ko zaroor batayein.
- COPD ke patients ko GERD (acid reflux) bhi ho sakta hai, chhote meals lein aur sone se 2-3 ghante pehle khana kha lein.
- Agar aapko neend mein saans phoolti hai ya aap thakaan mehsoos karte hain, sleep apnea ho sakta hai, doctor ko batayein.
- "COPD aapki life ka sirf ek hissa hai, poori kahani nahi. Hamesha yaad rakhna - aap COPD se bade hain, chhote nahi. Thodi si samajhdaari, thoda sa dhyan, aur apne aap par vishwaas...
Yahi teen cheezein aapko iske saath bhi khushhaal jeene ki taakat dengi.
- Take care, stay strong, and keep breathing easy! 🙏💙

"""

chat_session = model.start_chat(history=[
    {"role": "user", "parts": "System Instruction: " + SYSTEM_INSTRUCTION},
    {"role": "model", "parts": "Ok, main LungGuard hu."}
])

# 4. SERVER SETUP
app = FastAPI()

@app.post("/whatsapp")
async def reply_whatsapp(Body: str = Form(...), From: str = Form(...)):
    user_message = Body.strip()
    sender_number = From

    # Safe Printing (Emoji errors se bachne ke liye)
    try:
        print(f"Message from {sender_number}: {user_message}")
    except:
        print("Message received (Text hidden due to emoji error)")

    try:
        # AI se pucho
        response = chat_session.send_message(user_message)
        
        if response.parts:
            ai_reply_text = response.text
        else:
            ai_reply_text = "Maaf karein, main iska jawab nahi de sakta (Safety Policy)."
            
        try:
            print(f"AI Reply: {ai_reply_text}")
        except:
            print("AI Reply sent (Text hidden due to emoji error)")

    except Exception as e:
        print(f"Error: {e}")
        ai_reply_text = "Server abhi busy hai. Kripya thodi der baad try karein."

    # Twilio Response Container
    twilio_resp = MessagingResponse()
    twilio_resp.message(ai_reply_text)

    return Response(content=str(twilio_resp), media_type="application/xml")

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)





