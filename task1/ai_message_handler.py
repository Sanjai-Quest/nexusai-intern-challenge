import asyncio
import os
from dataclasses import dataclass
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@dataclass
class MessageResponse:
    response_text: str
    confidence: float
    suggested_action: str
    channel_formatted_response: str
    error: str | None

SYSTEM_PROMPT = """
You are a highly efficient Telecom Support Agent for 'Nexus Connect'. 
Your goal is to assist customers with billing, network issues, and service plans.

Voice Guidelines:
- Keep it brief (under 2 sentences).
- Sound natural and helpful.

Digital Guidelines (WhatsApp/Chat):
- Be more detailed.
- Use step-by-step instructions for technical issues.
- Use formatting (bolding) for clarity.

Rules:
1. Always be empathetic.
2. If the issue is a 'service_cancellation', acknowledge and prepare for escalation.
3. If data is missing, ask clearly.
4. Categorize the intent into: billing_issue, network_issue, technical_support, or service_cancellation.
"""

async def call_gemini(customer_message: str):
    """Internal function to call Gemini API with a timeout."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # We use asyncio.wait_for to handle the 10s timeout
    response = await asyncio.wait_for(
        asyncio.to_thread(model.generate_content, f"{SYSTEM_PROMPT}\n\nCustomer: {customer_message}"),
        timeout=10
    )
    return response.text

async def handle_message(customer_message: str, customer_id: str, channel: str) -> MessageResponse:
    """
    Processes a customer message and returns a structured response.
    Handles timeouts, rate limits, and empty inputs.
    """
    # (c) empty or whitespace-only input
    if not customer_message or not customer_message.strip():
        return MessageResponse(
            response_text="",
            confidence=0.0,
            suggested_action="none",
            channel_formatted_response="",
            error="empty_input"
        )

    try:
        # Initial attempt
        try:
            response_text = await call_gemini(customer_message)
        except Exception as e:
            # (b) API rate limit - retry once after 2 seconds
            # Note: Generic exception check as Gemini SDK error types can vary
            if "429" in str(e) or "rate" in str(e).lower():
                await asyncio.sleep(2)
                response_text = await call_gemini(customer_message)
            else:
                raise e

        # Mock extracting metadata from AI response
        # In a real scenario, we might use structured output or regex
        confidence = 0.92
        suggested_action = "provide_troubleshooting"
        
        if "cancel" in customer_message.lower():
            suggested_action = "escalate_to_retention"

        # Channel specific formatting
        if channel == "voice":
            # Ensure < 2 sentences
            sentences = response_text.split('.')
            formatted_response = '.'.join(sentences[:2]).strip()
            if not formatted_response.endswith('.'):
                formatted_response += '.'
        elif channel == "whatsapp":
            formatted_response = f"*Nexus Connect Support* 📱\n\n{response_text}"
        else:
            formatted_response = response_text

        return MessageResponse(
            response_text=response_text,
            confidence=confidence,
            suggested_action=suggested_action,
            channel_formatted_response=formatted_response,
            error=None
        )

    except asyncio.TimeoutError:
        # (a) API timeout after 10 seconds
        return MessageResponse(
            response_text="",
            confidence=0.0,
            suggested_action="retry",
            channel_formatted_response="",
            error="api_timeout"
        )
    except Exception as e:
        return MessageResponse(
            response_text="",
            confidence=0.0,
            suggested_action="manual_check",
            channel_formatted_response="",
            error=str(e)
        )

if __name__ == "__main__":
    # Quick local test
    async def test():
        resp = await handle_message("My internet is slow", "cust_123", "chat")
        print(resp)
    
    # asyncio.run(test())
