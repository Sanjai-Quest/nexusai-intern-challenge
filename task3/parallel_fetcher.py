import asyncio
import random
import time
import logging
from dataclasses import dataclass

# Setup logging for warnings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CustomerContext:
    crm_data: dict | None
    billing_data: dict | None
    ticket_history: dict | None
    data_complete: bool
    fetch_time_ms: float

async def fetch_crm(phone: str) -> dict:
    """Mock CRM fetch with 200–400ms delay."""
    delay = random.uniform(0.2, 0.4)
    await asyncio.sleep(delay)
    return {
        "customer_id": "cust_9988",
        "name": "Alex Johnson",
        "vip_status": random.choice([True, False]),
        "tier": "Gold"
    }

async def fetch_billing(phone: str) -> dict:
    """Mock billing system fetch with 150–350ms delay. 10% chance of TimeoutError."""
    delay = random.uniform(0.15, 0.35)
    await asyncio.sleep(delay)
    
    if random.random() < 0.10:
        raise TimeoutError("Billing system connection timed out")
        
    return {
        "balance": 45.50,
        "overdue": random.choice([True, False]),
        "last_payment": "2024-02-15"
    }

async def fetch_ticket_history(phone: str) -> dict:
    """Mock ticket history fetch with 100–300ms delay."""
    delay = random.uniform(0.1, 0.3)
    await asyncio.sleep(delay)
    return {
        "last_5_complaints": [
            {"id": "t1", "intent": "billing_issue", "status": "resolved"},
            {"id": "t2", "intent": "network_issue", "status": "escalated"},
            {"id": "t3", "intent": "network_issue", "status": "resolved"},
            {"id": "t4", "intent": "billing_issue", "status": "resolved"},
            {"id": "t5", "intent": "network_issue", "status": "resolved"}
        ],
        "total_tickets": 12
    }

async def fetch_sequential(phone: str):
    """Fetches data one by one."""
    start_time = time.perf_counter()
    
    try:
        crm = await fetch_crm(phone)
    except Exception:
        crm = None
        
    try:
        billing = await fetch_billing(phone)
    except Exception:
        billing = None
        
    try:
        tickets = await fetch_ticket_history(phone)
    except Exception:
        tickets = None
        
    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000
    print(f"Sequential Fetch Time: {duration_ms:.2f}ms")
    return crm, billing, tickets, duration_ms

async def fetch_parallel(phone: str) -> CustomerContext:
    """Fetches data in parallel using asyncio.gather."""
    start_time = time.perf_counter()
    
    # Use return_exceptions=True to prevent one failure from crashing the whole gather
    results = await asyncio.gather(
        fetch_crm(phone),
        fetch_billing(phone),
        fetch_ticket_history(phone),
        return_exceptions=True
    )
    
    crm_data = results[0] if not isinstance(results[0], Exception) else None
    billing_data = results[1] if not isinstance(results[1], Exception) else None
    ticket_history = results[2] if not isinstance(results[2], Exception) else None

    # Log warnings for failures
    if isinstance(results[0], Exception): logger.warning(f"CRM fetch failed: {results[0]}")
    if isinstance(results[1], Exception): logger.warning(f"Billing fetch failed: {results[1]}")
    if isinstance(results[2], Exception): logger.warning(f"Tickets fetch failed: {results[2]}")

    end_time = time.perf_counter()
    duration_ms = (end_time - start_time) * 1000
    print(f"Parallel Fetch Time: {duration_ms:.2f}ms")

    data_complete = all(not isinstance(r, Exception) for r in results)

    return CustomerContext(
        crm_data=crm_data,
        billing_data=billing_data,
        ticket_history=ticket_history,
        data_complete=data_complete,
        fetch_time_ms=duration_ms
    )

async def main():
    phone = "+1234567890"
    print("--- Starting Sequential Fetch ---")
    await fetch_sequential(phone)
    
    print("\n--- Starting Parallel Fetch ---")
    context = await fetch_parallel(phone)
    print(f"Data Complete: {context.data_complete}")

if __name__ == "__main__":
    asyncio.run(main())
