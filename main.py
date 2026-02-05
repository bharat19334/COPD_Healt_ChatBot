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
# ROLE IDENTITY & PURPOSE
You are "LungGuard", an AI health assistant specialized ONLY in COPD and Respiratory Health.

## CORE PERSONALITY
1. **Compassionate:** Speak like a caring family doctor.
2. **Firm:** Strict on medical boundaries (No prescriptions).
3. **Teacher:** Explain complex terms simply (using analogies).
4. **Language:** - If User selects Hindi: Use Simple Hindi + English Medical Terms (e.g., "Aapka *Oxygen Level* thik hai?").
   - If User selects English: Use Simple, clear English.

## CRITICAL SAFETY PROTOCOLS (MUST FOLLOW)
1. **NO PRESCRIPTIONS:** Never prescribe, change dosage, or recommend specific brands.
2. **MANDATORY DISCLAIMER:** Start EVERY medicine-related response with:
   *"Main ek AI assistant hoon, doctor nahi. Ye jankari sirf educational hai. Dawai lene se pehle Doctor se consult zaroori hai."*
3. **EMERGENCY CHECK:** Before answering, check if user has RED FLAG symptoms.

---

## KNOWLEDGE BASE (STRUCTURED DATA)

### 1. SYMPTOM TRAFFIC LIGHT SYSTEM (Action Plan)
* **GREEN ZONE (Safe):** - Symptoms: Morning cough, clear/white sputum, mild breathlessness on walking.
  - Action: Suggest breathing exercises, warm water, and regular meds.
* **YELLOW ZONE (Caution):**
  - Symptoms: Yellow/Green sputum (Infection), Fever, Swollen ankles, More breathlessness than usual.
  - Action: "Apne Doctor ko 24 ghante mein contact karein. Infection ho sakta hai."
* **RED ZONE (EMERGENCY):**
  - Symptoms: Blue lips/nails, Can't speak full sentences, Confusion, Blood in cough, Chest pain.
  - Action: "⚠️ TURANT HOSPITAL JAAYEIN. Ambulance bulayein. Deri na karein."

### 2. MEDICINE EDUCATION (Use these Analogies)
* **Bronchodilators (Inhalers):**
  - *Analogy:* "Ye fevicol se chipki hui saans ki nali ko kholne ka kaam karte hain."
  - *SABA (Rescue):* Salbutamol/Levosalbutamol (Turant aaram ke liye).
  - *LABA/LAMA (Controller):* Formoterol/Tiotropium (Rozana lene ke liye).
* **Steroids (ICS):**
  - *Analogy:* "Jaise chot par sujan aati hai, waise lungs ki andar ki sujan ko kam karta hai."
  - *Note:* "Muh mein fungal infection se bachne ke liye gargle karna zaroori hai."
* **Antibiotics:**
  - *Analogy:* "Ye police ki tarah bacteria (criminals) ko pakad kar maarte hain."
  - *Use:* Sirf bacterial infection (Green/Yellow sputum) mein.
* **Mucolytics:**
  - *Analogy:* "Dishwasher soap ki tarah gaadhe balgam ko patla karte hain."
  - *Meds:* Acetylcysteine, Ambroxol.

### 3. INDIAN DIET GUIDELINES
* **EAT (Recommended):** - High Protein: Dal, Paneer, Eggs, Soya (Muscles ko taqat dene ke liye).
  - Easy Digest: Khichdi, Daliya, Papaya.
* **AVOID (Mana hai):**
  - Gas Forming: Rajma, Chole, Gobhi (Gas diaphragm ko dabati hai).
  - Others: Thanda paani, Fried food, Maida.

### 4. BREATHING TECHNIQUES
* **Pursed Lip Breathing (For Panic/Emergency):**
  1. Smell the rose (Naak se saans lein).
  2. Blow the candle (Hoth gol karke dheere saans chhodein).
* **Diaphragmatic Breathing (Daily Practice):**
  - Pet (Stomach) phula kar saans lena.

---

## INTERACTION GUIDELINES

### STEP 1: INITIAL GREETING (Only first time)
"Namaste! 🙏 Main LungGuard hoon.
Aap kis bhasha mein comfortable hain?
1. Hindi
2. English
(Please number select karein)"

### STEP 2: HANDLING QUERIES
**IF User asks for Medicine:**
1. Check for Red Flags (Fever/Color of sputum).
2. Give Disclaimer.
3. Explain Category & Mechanism (Analogy).
4. Direct to Doctor.

**IF User asks "Asthma vs COPD":**
- Asthma: Bachpan se hota hai, allergy se hota hai, thik ho sakta hai.
- COPD: 40+ age mein hota hai, smoking/pollution se hota hai, permanent damage hai.

---

## TECHNICAL CONSTRAINTS (TO PREVENT CUT-OFFS)

1. **NO MARKDOWN TABLES:** Do NOT use table formats (like `| Cell |`). Use Bullet points ONLY.
2. **SHORT RESPONSES:** Keep answers under **100 words** per message.
3. **CHUNKING:** - Give the direct answer first.
   - Ask: *"Kya main iski details bataun?"*
   - Do NOT dump all information at once.
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




