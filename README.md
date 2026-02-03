# 🫁 AI-Powered COPD Health Assistant (WhatsApp Bot)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Twilio](https://img.shields.io/badge/Twilio-WhatsApp_API-red?logo=twilio)
![Gemini](https://img.shields.io/badge/AI-Google_Gemini-orange?logo=google)
![Status](https://img.shields.io/badge/Status-Active-success)

## 📌 Project Overview
This project is an intelligent **WhatsApp Chatbot** designed to assist patients and caregivers in understanding and managing **Chronic Obstructive Pulmonary Disease (COPD)**. 

Built as part of a project for **Technovation 2026** at **Career Point University**, this bot leverages the **Google Gemini API** to provide accurate, context-aware, and empathetic medical information in real-time. It aims to bridge the gap between complex medical data and patient accessibility.

## 🚀 Key Features
* **Real-time AI Responses:** Powered by Google's Gemini LLM for natural conversations.
* **WhatsApp Integration:** Uses Twilio to deliver health advice on the most accessible messaging platform.
* **24/7 Availability:** Instant answers to questions about symptoms, precautions, and lifestyle changes for COPD.
* **Secure Deployment:** Backend hosted on Render with secure API management.

## 🛠️ Tech Stack
* **Language:** Python
* **AI Model:** Google Gemini API
* **Messaging Service:** Twilio API (WhatsApp Sandbox/Production)
* **Backend Framework:** Flask / FastAPI
* **Deployment:** Render & Ngrok (for local tunneling)

## ⚙️ Architecture Flow
1.  **User** sends a message on WhatsApp.
2.  **Twilio** receives the message and sends a webhook POST request to the **Render** server.
3.  **Python Backend** processes the text and sends the query to **Gemini API**.
4.  **Gemini** generates a medically relevant response.
5.  **Twilio** sends the AI-generated response back to the user's WhatsApp.

## 🔧 Installation & Setup

### Prerequisites
* Python 3.x installed
* Twilio Account (SID & Auth Token)
* Google Gemini API Key

### Step 1: Clone the Repository
```bash
git clone [https://github.com/your-username/copd-chatbot.git](https://github.com/your-username/copd-chatbot.git)
cd copd-chatbot
