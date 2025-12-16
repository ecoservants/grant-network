-- ==========================================================
-- Open Grant Network
-- Reset / Teardown Script
-- ==========================================================
-- Drops all Grant Network tables safely
-- ==========================================================

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS community_job_results;
DROP TABLE IF EXISTS community_jobs;

SET FOREIGN_KEY_CHECKS = 1;
