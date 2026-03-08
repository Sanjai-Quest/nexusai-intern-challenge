# NexusAI Intern Challenge

This repository contains the completed tasks for the NexusAI Intern Challenge.

## Project Structure
- `task1/`: AI Message Handler (Google Gemini integration).
- `task2/`: PostgreSQL Database Schema and Repository.
- `task3/`: Parallel Data Fetcher (Performance demonstration).
- `task4/`: Escalation Decision Engine (Logic and Pytest).
- `ANSWERS.md`: Written design questions.

## Setup & Installation

1. **Clone the Repo:**
   ```bash
   git clone https://github.com/Sanjai-Quest/nexusai-intern-challenge.git
   cd nexusai-intern-challenge
   ```

2. **Environment Variables:**
   Create a `.env` file at the root with:
   ```env
   GEMINI_API_KEY=your_google_api_key_here
   # For Task 2 (if running repository tests)
   DATABASE_URL=postgres://user:password@localhost:5432/dbname
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Tasks

### Task 1: AI Message Handler
Located in `task1/ai_message_handler.py`. It uses `google-generativeai` to simulate a telecom support agent.

### Task 2: Database Schema
The SQL schema is in `task2/schema.sql`. The repository logic is in `task2/repository.py`.

### Task 3: Parallel Data Fetcher
Run the script to see the timing comparison:
```bash
python task3/parallel_fetcher.py
```
**Example Output:**
```text
--- Starting Sequential Fetch ---
Sequential Fetch Time: 845.20ms

--- Starting Parallel Fetch ---
Parallel Fetch Time: 382.15ms
Data Complete: True
```
*Observation:* Parallel fetching is ~2.2x faster as it only takes as long as the slowest request (CRM), whereas sequential takes the sum of all three.

### Task 4: Escalation Engine & Tests
Run the unit tests using pytest:
```bash
pytest task4/test_escalation.py -v
```

## Conflict Resolution Logic (Task 4)
In `task4/escalation_engine.py`, rules are checked in a specific priority order. 
- **Priority 1:** Critical Intents (e.g., `service_cancellation`) always win. Even if confidence is high (0.99), we escalate because the business value of a human retention agent is higher than AI efficiency.
- **Priority 2:** Safety/Sentiment. If a user is angry, we escalate immediately to prevent further brand damage.
- **Priority 3:** Data/Confidence. We only allow the AI to proceed if it has both the data AND the confidence to be helpful.
This hierarchy ensures high-risk situations are always handled by humans, while routine queries are automated.
