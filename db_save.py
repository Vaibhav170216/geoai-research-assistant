from datetime import datetime

from db_init import get_db_connection, DB_TIMEZONE


def save_conversation(record, question, application):
    """
    Save an LLM call record to PostgreSQL.

    Parameters
    ----------
    record : LLMCallRecord
        Metrics captured during the LLM call.
    question : str
        User's original question.
    application : str
        Name of the application (e.g. geoai-research-assistant).

    Returns
    -------
    int
        Database ID of the inserted record.
    """

    timestamp = datetime.now(DB_TIMEZONE)

    conn = get_db_connection()

    try:
        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO rag_requests (
                    question,
                    answer,
                    application,
                    model,
                    instructions,
                    prompt,
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                    response_time,
                    cost,
                    timestamp
                )
                VALUES (
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
                RETURNING id
                """,
                (
                    question,
                    record.answer,
                    application,
                    record.model,
                    record.instructions,
                    record.prompt,
                    record.prompt_tokens,
                    record.completion_tokens,
                    record.total_tokens,
                    record.response_time,
                    record.cost,
                    timestamp,
                ),
            )

            request_id = cur.fetchone()[0]

        conn.commit()

    finally:
        conn.close()

    return request_id