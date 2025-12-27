# Add this route below your opt_out function
@app.route('/compute/job', methods=['GET'])
def fetch_job():
    # 1. Auth via api_token (Requirement: Auth via api_token)
    api_token = request.headers.get('X-API-TOKEN')
    if not api_token:
        return jsonify({"error": "Unauthorized"}), 401

    db = phase2_db.get_db_connection()
    cur = db.cursor()

    try:
        # 2. Query & 3. Lock (Requirement: Query for pending job and lock it)
        # This uses "FOR UPDATE SKIP LOCKED" to prevent two nodes from taking the same job
        cur.execute("""
            UPDATE jobs 
            SET status = 'claimed', 
                claimed_by_node_id = (SELECT id FROM community_nodes WHERE api_token = %s),
                claimed_at = NOW()
            WHERE id = (
                SELECT id FROM jobs 
                WHERE status = 'pending' 
                LIMIT 1 
                FOR UPDATE SKIP LOCKED
            )
            RETURNING id, job_type, payload;
        """, (api_token,))
        
        job = cur.fetchone()
        db.commit()

        # 4. Return (Requirement: Return minimal JSON payload)
        if job:
            return jsonify({
                "job_id": job[0],
                "type": job[1],
                "data": job[2]
            }), 200
        else:
            return jsonify({"message": "No pending jobs"}), 404

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        db.close()
