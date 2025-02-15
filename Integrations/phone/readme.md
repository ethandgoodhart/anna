# Run concurrently:
node outbound.js

# example
curl -X POST https://ca55-2607-f6d0-ced-5bb-8598-b1fb-4ecc-dd05.ngrok-free.app/outbound-call \
-H "Content-Type: application/json" \
-d '{
    "prompt": "You are Eric, an outbound car sales agent. You are calling to sell a new car to the customer. Be friendly and professional and answer all questions.",
    "first_message": "Hello Thor, my name is Eric, I heard you were looking for a new car! What model and color are you looking for?",
    "number": "+14046635506"
}'

# .env setup
ELEVENLABS_AGENT_ID=...
ELEVENLABS_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...