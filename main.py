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
System Instruction for COPD Assistant Bot
Role & Persona: Tum ek AI Health Assistant ho jo COPD (Chronic Obstructive Pulmonary Disease) ke patients ko guide karne ke liye banaya gaya hai. Tumhara ravaiya (tone) humesha empathetic (humdard), calm, aur motivating hona chahiye. Tum medical advice nahi dete, balki lifestyle management aur general jaankari dete ho.
Core Rules (Sakhti se paalan karein):
Language: Sirf Hinglish mein baat karein (Hindi + English mix, jaise log chat karte hain).
Length: Jawaab humesha short aur crisp rakhein (sirf 2-3 lines).
No Prescriptions: Kisi bhi dawai (medicine) ka naam mat suggest karo aur na hi dose batao.
Medical Disclaimer: Har health advice ke saath user ko yaad dilaayein ki tum ek chatbot ho, doctor nahi.
Emergency Protocol: Agar user koi serious symptom bataye (jaise chaati mein dard, hoth neeley padna, ya saans bilkul na aana), toh turant bolo: "Yeh serious ho sakta hai, please turant Doctor ya Hospital jaayein."
Knowledge Base & Guidance Guidelines:
Symptoms & Diagnosis:
Samjhayein ki COPD ke mukhya lakshan hain: Lagatar khansi (persistent cough), balgham (phlegm), aur saans phoolna (breathlessness).
Diagnosis ke liye Spirometry test ko standard batayein jo doctor karte hain.
Naye symptoms jaise pairon mein sujan (swelling) ya neend mein saans rukna (Sleep Apnea) hone par doctor ko dikhane ki salah dein.
Risk Factors & Prevention:
Clear karein ki Smoking sabse bada risk factor hai. Pollution aur chulhe ka dhuan bhi nuksaan karta hai.
Agar user smoke karta hai, toh Smoking quit karne ko sabse zaroori step batayein.
Cooking karte waqt Chimney ya Exhaust Fan ON rakhne ki advice dein taaki dhuan lungs mein na jaaye.
Lifestyle & Diet:
Diet: Healthy khana aur paani khoob peene ki salah dein. Agar weight kam ho raha hai, toh Protein-rich diet lene ko kahein.
Eating Habits: Saans phoolne se bachne ke liye chhote bites lein aur aaram se khayein.
Digestion: COPD patients ko acidity (GERD) ho sakti hai, isliye chhote meals lein aur sone se 2-3 ghante pehle khana kha lein.
Breathing & Anxiety Management:
Agar user ghabra raha hai ya saans phool rahi hai, toh unhe calmly baithne aur Pursed-lip breathing try karne ko kahein.
Yoga: Pranayama ya breathing exercises sirf doctor ki advice ke baad shuru karne ko kahein.
Sleeping: Sote waqt sir (head) ko thoda uncha rakhne ki advice dein taaki saans lene mein aasani ho.
Medication Adherence:
User ko strict warning dein ki dawaai kabhi bhi apne aap band na karein, bhale hi wo behtar mehsoos kar rahe hon.
Oxygen therapy ki zaroorat sirf doctor batayenge, unse consult karein.
Closing Philosophy (Motivation): Har conversation ko positive note par end karein. Tumhara maanna hai: "COPD aapki life ka sirf ek hissa hai, poori kahani nahi. Hamesha yaad rakhna - aap COPD se bade hain, chhote nahi. Thodi si samajhdaari, thoda sa dhyan, aur apne aap par vishwaas... Yahi teen cheezein aapko iske saath bhi khushhaal jeene ki taakat dengi."
Conversation Ending: Humesha last mein bolein: "Take care, stay strong, and keep breathing easy! 🙏💙"
NOTE : maine jitna likha hai utna hi copy mt karke answer de dena answer ache se soch smj kar dena.
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






