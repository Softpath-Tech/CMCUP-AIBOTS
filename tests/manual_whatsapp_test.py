import requests
import json

base_url = "http://localhost:8000"

def test_whatsapp(message, phone):
    print(f"\n🔹 TESTING /whatsappchat: '{message}' (Phone: {phone})")
    try:
        url = f"{base_url}/whatsappchat"
        # WhatsAppChatRequest: user_message, phone_number
        payload = {"user_message": message, "phone_number": phone}
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        print(f"🔸 Response: {data.get('response', 'No response field')}")
        return data
    except Exception as e:
        print(f"❌ Error: {e}")

print("🚀 Starting WhatsApp Logic Verification")

# Test /whatsappchat (Menu Logic - Should now work!)
# Using phone number as session ID
phone_user = "919876543210"
test_whatsapp("Hi", phone_user)
test_whatsapp("1", phone_user) 
