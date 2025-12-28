def store_job_result(cur, job_id, node_id, result_json, checksum):
    """Save job result and mark job completed"""

    # Insert into results table
    cur.execute("""
        INSERT INTO community_job_results (job_id, node_id, result_json, result_checksum, status, created_at)
        VALUES (%s, %s, %s, %s, 'submitted', NOW())
    """, (job_id, node_id, str(result_json), checksum))

    # Mark job completed
    cur.execute("""
        UPDATE community_jobs
        SET status='completed', completed_at=NOW()
        WHERE id = %s
    """, (job_id,))
