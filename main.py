import os
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import uvicorn
from groq import Groq  # Google ki jagah Groq import kiya

# 1. SETUP
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("❌ Error: GROQ API Key nahi mili! .env file check karein.")
else:
    print("✅ Groq API Key loaded successfully.")

# 2. CLIENT CONFIGURATION
client = Groq(api_key=GROQ_API_KEY)

# 3. SYSTEM INSTRUCTION (Same as before)
SYSTEM_INSTRUCTION = """
ROLE: Tumhara naam 'COPD Assistant' hai. Tum ek expert COPD Health Assistant ho.
GUIDELINES: 
- Hinglish mein baat karo. 
- Jawab short (5-7) line mein do.
- Dawai (Medicine) prescribe mat karo.
- Agar koi serious symptom bataye to bolo 'Turant Doctor ke paas jao'.
- Iske mukhya symptoms hain: lagatar khansi, balgham aur saans phoolna.
- "COPD aapki life ka sirf ek hissa hai, poori kahani nahi. Hamesha yaad rakhna - aap COPD se bade hain, chhote nahi."
- Agar koi copd se related nhi ho toh usse bolo ki ye copd se related nhi hai.
"""

# Global Chat History (Simple List)
# Isme hum system instruction pehle hi daal dete hain
chat_history = [
    {"role": "system", "content": SYSTEM_INSTRUCTION}
]

# 4. SERVER SETUP
app = FastAPI()

@app.post("/whatsapp")
async def reply_whatsapp(Body: str = Form(...), From: str = Form(...)):
    user_message = Body.strip()
    sender_number = From

    print(f"📩 Message from {sender_number}: {user_message}")

    # --- MEMORY MANAGEMENT (CRITICAL FIX) ---
    # 1. User ka message history mein add karo
    chat_history.append({"role": "user", "content": user_message})

    # 2. ROLLING WINDOW: Agar history 12 messages se badi ho gayi, toh purane delete karo
    # Hum index 1 se delete karenge taaki 'System Instruction' (index 0) hamesha rahe.
    if len(chat_history) > 12:
        # Syntax: [System Instruction] + [Last 10 messages]
        # Ye purani baatein bhula dega taaki bot hang na ho
        chat_history[:] = [chat_history[0]] + chat_history[-10:]

    try:
        # --- GROQ API CALL ---
        chat_completion = client.chat.completions.create(
            messages=chat_history,
            model="llama-3.3-70b-versatile",  # High quality & Fast model
            temperature=0.7,
            max_tokens=200,
        )

        ai_reply_text = chat_completion.choices[0].message.content
        print(f"🤖 AI Reply: {ai_reply_text}")

        # AI ka jawab bhi history mein add karo taaki context bana rahe
        chat_history.append({"role": "assistant", "content": ai_reply_text})

    except Exception as e:
        print(f"❌ Error: {e}")
        ai_reply_text = "Server abhi busy hai. Kripya thodi der baad try karein."

    # Twilio Response
    twilio_resp = MessagingResponse()
    twilio_resp.message(ai_reply_text)

    return Response(content=str(twilio_resp), media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
