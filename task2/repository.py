import asyncpg
from datetime import datetime, timedelta

class CallRecordRepository:
    """
    Repository for managing customer interaction records in PostgreSQL.
    Uses asyncpg for high-performance async database operations.
    """

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def save(self, call_data: dict):
        """
        Saves a single interaction record.
        Uses parameterized queries to prevent SQL injection.
        """
        query = """
            INSERT INTO call_records (
                customer_phone, channel, transcript, ai_response, 
                intent, outcome, confidence_score, csat_score, duration_seconds
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """
        async with self.pool.acquire() as connection:
            await connection.execute(
                query,
                call_data['customer_phone'],
                call_data['channel'],
                call_data['transcript'],
                call_data['ai_response'],
                call_data.get('intent'),
                call_data['outcome'],
                call_data['confidence_score'],
                call_data.get('csat_score'),
                call_data['duration_seconds']
            )

    async def get_recent(self, phone: str, limit: int = 5) -> list:
        """
        Retrieves the most recent interactions for a given phone number.
        """
        query = """
            SELECT * FROM call_records 
            WHERE customer_phone = $1 
            ORDER BY created_at DESC 
            LIMIT $2
        """
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, phone, limit)
            # Convert Record objects to dictionaries
            return [dict(row) for row in rows]

async def lowest_resolution_intents(pool: asyncpg.Pool) -> list:
    """
    Returns the top 5 intent types with the lowest resolution rate in the last 7 days.
    Also returns their average CSAT.
    """
    query = """
        SELECT 
            intent,
            AVG(csat_score) as avg_csat,
            ROUND(
                (SUM(CASE WHEN outcome = 'resolved' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*)) * 100, 
                2
            ) as resolution_rate
        FROM call_records
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY intent
        HAVING intent IS NOT NULL
        ORDER BY resolution_rate ASC
        LIMIT 5
    """
    async with pool.acquire() as connection:
        rows = await connection.fetch(query)
        return [dict(row) for row in rows]
