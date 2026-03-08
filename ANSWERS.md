# Task 5 — Written Design Questions

### Q1: STT Partial Transcripts Approach
Querying the database on partial transcripts (every 200ms) follows a "speculative execution" pattern. The main advantage is **latency reduction**; by the time the user stops talking, the AI might already have fetched relevant account details or billing history. This makes the response feel instantaneous.

However, the tradeoffs are significant. First, **resource wastage** is high; most partial queries will be based on incomplete or misunderstood intent, leading to unnecessary database load. Second, **noisy context** can occur if a partial phrase (e.g., "I want to pay...") is misinterpreted before the full sentence ("I want to pay... with a different card next month") is finished.

**My Approach:** I suggest a hybrid "debounced" approach. We shouldn't query every 200ms. Instead, we should wait for a "semantic landmark" or a pause of at least 500-800ms, or when the STT confidence for a specific intent exceeds a threshold. We can speculatively fetch *non-destructive* data (like customer profile) but wait for the "End of Speech" (VAD) marker before triggering expensive AI reasoning or database writes. This balances speed with system efficiency.

### Q2: Knowledge Base Auto-Addition Risks
Automatically adding resolutions with CSAT ≥ 4 to a knowledge base (KB) sounds efficient but has two major risks over 6 months:

1.  **Hallucination Persistence:** An AI might provide a "successful" resolution that is factually wrong or creates a security loophole (e.g., accidentally revealing how to bypass a fee), and the customer gives a 5-star rating simply because they "saved money." Over time, the KB becomes filled with "incorrect but popular" shortcuts. 
    *   *Prevention:* Implement an "Expert-in-the-loop" verification step. High-CSAT resolutions are marked as "Pending Review" and must be verified by a human senior agent before appearing in the public KB.
2.  **Stale Policy Drift:** Telecom plans and technical steps change frequently. A resolution that worked in January might be invalid in June due to a software update or a new system rollout. 
    *   *Prevention:* Add a "TTL" (Time-to-Live) or "Periodic Audit" flag to KB entries. Any auto-added entry older than 90 days is hidden until re-validated against current company policy. We can also use an "LLM Auditor" to check if the KB entry conflicts with the *current* master documentation.

### Q3: Step-by-Step AI Handling
When a customer says: *"I've been without internet for 4 days, I called 3 times already, your company is useless and I want to cancel right now."*

1.  **Sentiment Analysis:** The AI immediately detects a sentiment score of -0.9 (extreme frustration).
2.  **Intent Detection:** Primary intent is `service_cancellation`, secondary is `network_issue`.
3.  **Context Retrieval:** The AI fetches the ticket history and sees 3 previous calls (matching Rule 3: repeat complaint).
4.  **Escalation Decision:** The `should_escalate` logic triggers multiple rules (Rule 2: Angry, Rule 3: Repeat, Rule 4: Cancellation).
5.  **AI Response:** Instead of trying to fix the internet, the AI says: *"I am very sorry for the frustration this has caused, especially since you've reached out three times already. I see your service has been down for 4 days. I am transferring you immediately to our Loyalty & Retention specialist who can prioritize your fix and discuss account credits."*
6.  **Handover to Human:** The AI passes a structured context to the agent:
    *   *Customer Status:* Frustrated / High Churn Risk.
    *   *Reason:* 4-day outage, 3 failed previous attempts.
    *   *Action:* Transferring for retention and priority dispatch.

### Q4: The Most Important Improvement
The single most important addition would be **"Proactive Contextual Grounding"** via a Graph Database (like Neo4j) for the Knowledge Base.

Currently, most systems use RAG (Vector Search) which finds similar text but doesn't understand *relationships*. A Graph-based KB would connect a "Network Outage" node to "Geographic Location" and "Specific Router Model." 

**How to build it:** I would map our existing documentation into a Knowledge Graph. When a user calls, the AI wouldn't just look for "No internet" keywords; it would check if there is an active "Incident" node connected to the user's specific exchange or neighborhood.

**Measurement:** We would measure success through **"Reduction in Average Handle Time (AHT)"** and **"First Call Resolution (FCR)"**. If the AI can tell a user *"I see an outage in your specific block (Sector 12) affecting 50 others,"* it avoids 10 minutes of useless troubleshooting steps. We would compare FCR for users handled with Graph-knowledge vs. standard RAG.
